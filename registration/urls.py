from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.registration_view, name='register'),
    path('public/register/', views.public_registration_view, name='public_register'),
    path('admin/', views.index, name='index'),
    path('lobby/', views.lobby_dashboard, name='lobby_dashboard'),
    path('personnel/', views.create_personnel_view, name='create_personnel'),
    path('personnel/<int:user_id>/', views.guard_info_view, name='guard_info'),
    path('personnel/<int:user_id>/reset-password/', views.reset_guard_password_view, name='reset_guard_password'),
    path('guests/', views.guestlist_view, name='guestlist'),
    path('guestlist/', views.guestlist_view, name='guestlist'),
	
]