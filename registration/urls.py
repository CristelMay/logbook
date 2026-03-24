from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
	path('register/', views.registration_view, name='register'),
	path('login/', views.login_view, name='login'),
	path('personnel/', views.create_personnel_view, name='create_personnel'),
]