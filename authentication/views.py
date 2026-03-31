from django.contrib import messages
from django.contrib.messages import get_messages
from django.db import DatabaseError
from django.db import connection
from django.shortcuts import redirect, render


def get_auth_state(request):
    return {
        'user_id': request.session.get('user_id'),
        'username': request.session.get('username'),
        'role_name': request.session.get('role_name'),
        'profile_pic': request.session.get('profile_pic'),
        'is_temp_password': request.session.get('is_temp_password', False),
    }


def _clear_messages(request):
    # Consume any queued messages so unrelated old flashes do not reappear.
    list(get_messages(request))


def _build_name_fallbacks(username):
    base = (username or 'User').replace('.', ' ').replace('_', ' ').strip()
    title_name = base.title() if base else 'User'
    first_name = title_name.split()[0] if title_name else 'User'
    return first_name, title_name


def login_handler(request, template_name='registration/login.html'):
    context = {'form_data': {}}

    if request.method == 'GET':
        _clear_messages(request)

    auth_state = get_auth_state(request)
    if auth_state.get('user_id'):
        role_name = auth_state.get('role_name')
        is_temp_password = auth_state.get('is_temp_password', False)
        if is_temp_password and role_name == 'guard':
            return redirect('registration:lobby_dashboard')
        if is_temp_password:
            return redirect('registration:change_password')
        if role_name == 'admin':
            return redirect('registration:index')
        if role_name == 'guard':
            return redirect('registration:lobby_dashboard')

    if request.method == 'POST':
        _clear_messages(request)
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        context['form_data'] = {'username': username}

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, template_name, context)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT user_id, username, role_name, profile_pic, is_active, is_tempPassword
                    FROM login_user(%s, %s);
                    """,
                    [username, password],
                )
                user = cursor.fetchone()
        except DatabaseError:
            messages.error(request, 'Login is unavailable right now. Please try again.')
            return render(request, template_name, context)

        if not user:
            messages.error(request, 'Invalid username or password.')
            return render(request, template_name, context)

        user_id, db_username, role_name, profile_pic, is_active, is_temp_password = user

        if not is_active:
            messages.error(request, 'This account is inactive. Please contact admin.')
            return render(request, template_name, context)

        auth_state = {
            'user_id': user_id,
            'username': db_username,
            'role_name': role_name,
            'profile_pic': profile_pic,
            'is_temp_password': is_temp_password,
        }

        display_name, full_name = _build_name_fallbacks(db_username)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.firstname, p.lastname
                FROM users u
                JOIN person p ON u.person_id = p.person_id
                WHERE u.user_id = %s;
                """,
                [user_id],
            )
            person_row = cursor.fetchone()

        if person_row and person_row[0] and person_row[1]:
            display_name = str(person_row[0]).strip().title()
            full_name = f"{str(person_row[0]).strip().title()} {str(person_row[1]).strip().title()}"

        request.session['user_id'] = auth_state['user_id']
        request.session['username'] = auth_state['username']
        request.session['role_name'] = auth_state['role_name']
        request.session['profile_pic'] = auth_state['profile_pic']
        request.session['is_temp_password'] = auth_state['is_temp_password']
        request.session['display_name'] = display_name
        request.session['full_name'] = full_name

        if is_temp_password and role_name == 'guard':
            return redirect('registration:lobby_dashboard')

        if is_temp_password:
            return redirect('registration:change_password')

        if role_name == 'admin':
            return redirect('registration:index')

        if role_name == 'guard':
            return redirect('registration:lobby_dashboard')

        request.session.flush()
        messages.error(request, 'Unauthorized role. Please contact admin.')
        return render(request, template_name, context)

    return render(request, template_name, context)


def change_password_handler(request, template_name, extra_context=None):
    context = extra_context or {}
    auth_state = get_auth_state(request)
    user_id = auth_state.get('user_id')
    is_temp_password = bool(auth_state.get('is_temp_password', False))

    if not user_id:
        return redirect('registration:login')

    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            valid = True

            if not is_temp_password:
                if not old_password:
                    messages.error(request, 'Current password is required.')
                    valid = False

            if valid and not is_temp_password:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT 1 FROM users WHERE user_id = %s AND password_hash = crypt(%s, password_hash);",
                            [user_id, old_password],
                        )
                        valid = cursor.fetchone() is not None
                except DatabaseError:
                    valid = False

                if not valid:
                    messages.error(request, 'Current password is incorrect.')

            if valid:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE users
                            SET password_hash = crypt(%s, gen_salt('bf')),
                                is_tempPassword = FALSE
                            WHERE user_id = %s;
                            """,
                            [new_password, user_id],
                        )

                    auth_state['is_temp_password'] = False
                    request.session['is_temp_password'] = False

                    from django.contrib import messages as django_messages
                    django_messages.success(request, 'Password changed successfully.')

                    return redirect('registration:edit_profile', guest_id=user_id)
                except DatabaseError:
                    messages.error(request, 'Unable to update password right now. Please try again.')

    context['show_change_password_modal'] = True
    return render(request, template_name, context)


def logout_handler(request):
    _clear_messages(request)
    request.session.flush()
    return redirect('registration:login')
