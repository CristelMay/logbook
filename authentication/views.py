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
        'is_temp_password': request.session.get('is_temp_password', False),
    }


def _clear_messages(request):
    # Consume any queued messages so unrelated old flashes do not reappear.
    list(get_messages(request))


def login_handler(request, template_name='registration/login.html'):
    context = {'form_data': {}}

    if request.method == 'GET':
        _clear_messages(request)

    auth_state = get_auth_state(request)
    if auth_state.get('user_id'):
        role_name = auth_state.get('role_name')
        is_temp_password = auth_state.get('is_temp_password', False)
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
                    SELECT user_id, username, role_name, is_active, is_tempPassword
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

        user_id, db_username, role_name, is_active, is_temp_password = user

        if not is_active:
            messages.error(request, 'This account is inactive. Please contact admin.')
            return render(request, template_name, context)

        auth_state = {
            'user_id': user_id,
            'username': db_username,
            'role_name': role_name,
            'is_temp_password': is_temp_password,
        }

        request.session['user_id'] = auth_state['user_id']
        request.session['username'] = auth_state['username']
        request.session['role_name'] = auth_state['role_name']
        request.session['is_temp_password'] = auth_state['is_temp_password']

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


def change_password_handler(request, template_name='authentication/change-password.html'):
    auth_state = get_auth_state(request)
    user_id = auth_state.get('user_id')

    if not user_id:
        return redirect('registration:login')

    if request.method == 'POST':
        _clear_messages(request)
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, template_name)

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, template_name)

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

        role_name = auth_state.get('role_name')
        if role_name == 'admin':
            return redirect('registration:index')
        if role_name == 'guard':
            return redirect('registration:lobby_dashboard')

        request.session.flush()
        return render(request, '404.html', status=404)

    return render(request, template_name)


def logout_handler(request):
    _clear_messages(request)
    request.session.flush()
    return redirect('registration:login')
