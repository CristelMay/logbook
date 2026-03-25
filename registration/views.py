from django.db import DatabaseError, IntegrityError
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
import logging
from PIL import Image
from PIL import UnidentifiedImageError
from io import BytesIO
import secrets
import string

from authentication.decorators import role_required
from authentication.views import (
    change_password_handler,
    login_handler,
    logout_handler,
)
from .models import (
    create_user_account,
    get_dashboard_stats,
    get_guard_info,
    get_recent_checkouts,
    get_today_visitor_log,
    reset_user_password,
    username_exists,
    view_all_guards,
)
from .services import create_guest_visit
from .storage import get_profile_image_url, upload_profile_image
from .validators import validate_guest_registration_payload


logger = logging.getLogger(__name__)


def login_view(request):
    return login_handler(request, template_name='registration/login.html')


def change_password_view(request):
    return change_password_handler(request)


def logout_view(request):
    return logout_handler(request)

@role_required('admin')
def index(request):
    stats = {
        'total_today': 0,
        'currently_inside': 0,
        'checked_out_today': 0,
        'total_this_month': 0,
    }
    recent_checkouts = []
    recent_checkouts_error = None
    today_visitor_log = []
    today_visitor_log_error = None

    try:
        stats = get_dashboard_stats()
    except DatabaseError:
        pass

    try:
        recent_checkouts = get_recent_checkouts()
    except DatabaseError as exc:
        recent_checkouts_error = str(exc)
        logger.exception('Failed to fetch recent check-outs')

    try:
        today_visitor_log = get_today_visitor_log()
    except DatabaseError as exc:
        today_visitor_log_error = str(exc)
        logger.exception("Failed to fetch today's visitor log")

    return render(
        request,
        "registration/admin-dashboard.html",
        {
            'stats': stats,
            'recent_checkouts': recent_checkouts,
            'recent_checkouts_error': recent_checkouts_error,
            'today_visitor_log': today_visitor_log,
            'today_visitor_log_error': today_visitor_log_error,
        },
    )

@role_required('guard')
def lobby_dashboard(request):
    require_password_change = bool(request.session.get('is_temp_password'))

    if request.method == 'POST' and require_password_change:
        return change_password_handler(
            request,
            template_name='registration/lobby-dashboard.html',
            extra_context={'require_password_change': True},
        )

    context = {
        'require_password_change': require_password_change,
    }
    return render(request, "registration/lobby-dashboard.html", context)

@role_required('admin', 'guard')
def registration_view(request):
    return _handle_registration_submission(
        request,
        success_redirect_name='registration:register',
    )


def public_registration_view(request):
    return _handle_registration_submission(
        request,
        success_redirect_name='registration:public_register',
    )


def _handle_registration_submission(request, success_redirect_name):
    context = {
        'form_data': {},
        'errors': {},
        'form_action_name': success_redirect_name,
    }

    if request.method == 'POST':
        cleaned_data, errors = validate_guest_registration_payload(request.POST)
        context['form_data'] = request.POST
        context['errors'] = errors

        if not errors:
            try:
                create_guest_visit(cleaned_data)
                messages.success(
                    request,
                    'Registration submitted successfully.'
                )
                return redirect(success_redirect_name)
            except DatabaseError:
                context['errors']['non_field'] = (
                    'Unable to save guest visit right now. Please try again.'
                )

    return render(request, 'registration/registration.html', context)

@role_required('admin')
def create_personnel_view(request):
    created_account = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        temporary_password = request.POST.get('temporary_password', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        middle_initial = request.POST.get('middle_initial', '').strip()
        suffix = request.POST.get('suffix', '').strip()
        profile_pic_file = request.FILES.get('profile_pic')

        if not username or not last_name or not first_name:
            messages.error(request, 'First name, last name, and username are required.')
        elif username_exists(username):
            messages.error(request, f'Username "{username}" is already taken. Please choose a different username.')
        elif not profile_pic_file:
            messages.error(request, 'Profile photo is required.')
        else:
            try:
                image_bytes, content_type = _validate_profile_image(profile_pic_file)
                profile_pic_path = upload_profile_image(
                    file_bytes=image_bytes,
                    original_name=profile_pic_file.name,
                    content_type=content_type,
                )

                if not temporary_password.startswith('Temp@'):
                    temporary_password = _generate_temp_password()

                create_user_account(
                    username=username,
                    password=temporary_password,
                    role_id=2,
                    last_name=last_name,
                    first_name=first_name,
                    middle_initial=middle_initial or None,
                    suffix=suffix or None,
                    profile_pic=profile_pic_path,
                )

                created_account = {
                    'username': username,
                    'temporary_password': temporary_password,
                }
                messages.success(request, 'Lobby personnel account created successfully.')
            except ValueError as exc:
                messages.error(request, str(exc))
            except IntegrityError as exc:
                if _is_username_unique_violation(exc):
                    messages.error(request, f'Username "{username}" is already taken. Please choose a different username.')
                else:
                    messages.error(request, 'Unable to create account right now. Please try again.')
            except DatabaseError:
                messages.error(request, 'Unable to create account right now. Please try again.')

    guards = view_all_guards()
    for guard in guards:
        guard['profile_pic'] = get_profile_image_url(guard.get('profile_pic'))

    context = {
        'guards': guards,
        'created_account': created_account,
    }
    return render(request, 'registration/create-personnel.html', context)


@role_required('admin')
def guard_info_view(request, user_id):
    guard = get_guard_info(user_id)
    if not guard:
        return JsonResponse({'detail': 'Guard not found.'}, status=404)

    guard['profile_pic'] = get_profile_image_url(guard.get('profile_pic'))

    return JsonResponse(guard)


def _generate_temp_password(length=10):
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f'Temp@{random_part}'


def _validate_profile_image(uploaded_file):
    allowed_formats = {
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
        'WEBP': 'image/webp',
    }

    file_bytes = uploaded_file.read()
    if not file_bytes:
        raise ValueError('Uploaded image is empty.')

    try:
        image = Image.open(BytesIO(file_bytes))
        image_format = (image.format or '').upper()
    except UnidentifiedImageError as exc:
        raise ValueError('Invalid image file. Please upload JPG, PNG, or WEBP.') from exc

    if image_format not in allowed_formats:
        raise ValueError('Unsupported image format. Please upload JPG, PNG, or WEBP.')

    return file_bytes, allowed_formats[image_format]


def _is_username_unique_violation(exc):
    cause = getattr(exc, '__cause__', None)
    pg_code = getattr(cause, 'pgcode', '')
    if pg_code == '23505':
        return True

    text = str(exc).lower()
    return 'duplicate key value violates unique constraint' in text and 'username' in text


@role_required('admin')
def reset_guard_password_view(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed.'}, status=405)

    guard = get_guard_info(user_id)
    if not guard:
        return JsonResponse({'detail': 'Guard not found.'}, status=404)

    temporary_password = _generate_temp_password()

    try:
        message = reset_user_password(user_id, temporary_password)
    except DatabaseError:
        return JsonResponse({'detail': 'Unable to reset password right now.'}, status=500)

    return JsonResponse(
        {
            'message': message or 'Temporary password has been set',
            'username': guard['username'],
            'temporary_password': temporary_password,
        }
    )

def guestlist_view(request):
    return render(request, 'registration/guestlist.html')
