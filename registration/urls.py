from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.registration_view, name='register'),
    path('admin/', views.index, name='index'),
    path('lobby/', views.lobby_dashboard, name='lobby_dashboard'),
    path('personnel/', views.create_personnel_view, name='create_personnel'),
	
]