from django.db import DatabaseError
from django.contrib import messages
from django.shortcuts import redirect, render

from authentication.decorators import role_required
from authentication.views import (
    change_password_handler,
    login_handler,
    logout_handler,
)
from .services import create_guest_visit
from .validators import validate_guest_registration_payload


def login_view(request):
    return login_handler(request, template_name='registration/login.html')


def change_password_view(request):
    return change_password_handler(request)


def logout_view(request):
    return logout_handler(request)

@role_required('admin')
def index(request):
    return render(request, "registration/admin-dashboard.html")

@role_required('guard')
def lobby_dashboard(request):
    return render(request, "registration/lobby-dashboard.html")

@role_required('admin', 'guard')
def registration_view(request):
    context = {
        'form_data': {},
        'errors': {},
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
                return redirect('registration:register')
            except DatabaseError:
                context['errors']['non_field'] = (
                    'Unable to save guest visit right now. Please try again.'
                )

    return render(request, 'registration/registration.html', context)

@role_required('admin')
def create_personnel_view(request):
    return render(request, 'registration/create-personnel.html')

def guestlist_view(request):
    return render(request, 'registration/guestlist.html')

def guestlist_view (request):
    return render(request, 'registration/guestlist.html')
