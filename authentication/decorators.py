from functools import wraps

from django.shortcuts import redirect, render
from .views import get_auth_state


def role_required(*allowed_roles):
    """Require authenticated cookie state and optionally restrict by role."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            auth_state = get_auth_state(request) or {}
            user_id = auth_state.get('user_id')
            role_name = auth_state.get('role_name')
            is_temp_password = auth_state.get('is_temp_password', False)
            url_name = request.resolver_match.url_name if request.resolver_match else None

            if not user_id or not role_name:
                return redirect('registration:login')

            # Guard users complete first-login password reset inside lobby dashboard modal.
            allow_guard_lobby_modal = role_name == 'guard' and url_name == 'lobby_dashboard'
            if is_temp_password and url_name != 'change_password' and not allow_guard_lobby_modal:
                return redirect('registration:change_password')

            if allowed_roles and role_name not in allowed_roles:
                return render(request, '404.html', status=404)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
