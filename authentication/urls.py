from django.urls import path

from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
]
