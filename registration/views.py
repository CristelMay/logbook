
from django.shortcuts import render

def registration_view(request):
	return render(request, 'registration/registration.html')