from .storage import get_profile_image_url


def auth_nav_context(request):
    role_name = request.session.get('role_name')
    username = request.session.get('username')
    profile_pic = request.session.get('profile_pic')
    display_name = request.session.get('display_name')
    full_name = request.session.get('full_name')

    if not display_name and username:
        base = username.replace('.', ' ').replace('_', ' ').strip()
        display_name = base.title().split()[0] if base else 'User'

    if not full_name and username:
        base = username.replace('.', ' ').replace('_', ' ').strip()
        full_name = base.title() if base else 'User'

    try:
        profile_image_url = get_profile_image_url(profile_pic)
    except Exception:
        profile_image_url = ''

    return {
        'current_role': role_name,
        'current_username': username,
        'current_profile_image_url': profile_image_url,
        'current_display_name': display_name or 'User',
        'current_full_name': full_name or 'User',
        'is_admin_role': role_name == 'admin',
        'is_guard_role': role_name == 'guard',
    }
