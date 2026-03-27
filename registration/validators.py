# from django.core.exceptions import ValidationError
# from django.core.validators import validate_email


# def _clean_text(value):
#     if value is None:
#         return ''
#     return str(value).strip()


# def validate_guest_registration_payload(payload):
#     errors = {}

#     lastname = _clean_text(payload.get('lastname'))
#     firstname = _clean_text(payload.get('firstname'))
#     middle_initial = _clean_text(payload.get('middle_initial'))
#     suffix = _clean_text(payload.get('suffix'))
#     contact_number = _clean_text(payload.get('contact_number'))
#     email = _clean_text(payload.get('email'))
#     company_name = _clean_text(payload.get('company_name'))
#     contact_name = _clean_text(payload.get('contact_name'))
#     purpose_name = _clean_text(payload.get('purpose_name'))

#     if not lastname:
#         errors['lastname'] = 'Last name is required.'
#     elif len(lastname) > 100:
#         errors['lastname'] = 'Last name must be at most 100 characters.'

#     if not firstname:
#         errors['firstname'] = 'First name is required.'
#     elif len(firstname) > 100:
#         errors['firstname'] = 'First name must be at most 100 characters.'

#     if middle_initial and len(middle_initial) > 5:
#         errors['middle_initial'] = 'Middle initial must be at most 5 characters.'

#     if suffix and len(suffix) > 10:
#         errors['suffix'] = 'Suffix must be at most 10 characters.'

#     if not contact_number:
#         errors['contact_number'] = 'Contact number is required.'
#     elif len(contact_number) > 20:
#         errors['contact_number'] = 'Contact number must be at most 20 characters.'

#     if email:
#         if len(email) > 150:
#             errors['email'] = 'Email must be at most 150 characters.'
#         else:
#             try:
#                 validate_email(email)
#             except ValidationError:
#                 errors['email'] = 'Enter a valid email address.'

#     if not company_name:
#         errors['company_name'] = 'Company is required.'
#     elif len(company_name) > 150:
#         errors['company_name'] = 'Company name must be at most 150 characters.'

#     if not contact_name:
#         errors['contact_name'] = 'Contact person is required.'
#     elif len(contact_name) > 150:
#         errors['contact_name'] = 'Contact person must be at most 150 characters.'

#     if not purpose_name:
#         errors['purpose_name'] = 'Purpose is required.'
#     elif len(purpose_name) > 150:
#         errors['purpose_name'] = 'Purpose must be at most 150 characters.'

#     cleaned_data = {
#         'lastname': lastname,
#         'firstname': firstname,
#         'middle_initial': middle_initial or None,
#         'suffix': suffix or None,
#         'contact_number': contact_number,
#         'email': email or None,
#         'company_name': company_name,
#         'contact_name': contact_name,
#         'purpose_name': purpose_name,
#     }

#     return cleaned_data, errors


import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Add this constant at the top
PHONE_REGEX = re.compile(r'^[0-9]{11}$')  # Exactly 11 digits

def _clean_text(value):
    if value is None:
        return ''
    return str(value).strip()


def validate_guest_registration_payload(payload):
    errors = {}

    lastname = _clean_text(payload.get('lastname'))
    firstname = _clean_text(payload.get('firstname'))
    middle_initial = _clean_text(payload.get('middle_initial'))
    suffix = _clean_text(payload.get('suffix'))
    contact_number = _clean_text(payload.get('contact_number'))
    email = _clean_text(payload.get('email'))
    company_name = _clean_text(payload.get('company_name'))
    contact_name = _clean_text(payload.get('contact_name'))
    purpose_name = _clean_text(payload.get('purpose_name'))

    if not lastname:
        errors['lastname'] = 'Last name is required.'
    elif len(lastname) > 100:
        errors['lastname'] = 'Last name must be at most 100 characters.'

    if not firstname:
        errors['firstname'] = 'First name is required.'
    elif len(firstname) > 100:
        errors['firstname'] = 'First name must be at most 100 characters.'

    if middle_initial and len(middle_initial) > 5:
        errors['middle_initial'] = 'Middle initial must be at most 5 characters.'

    if suffix and len(suffix) > 10:
        errors['suffix'] = 'Suffix must be at most 10 characters.'

    # Updated contact number validation
    if not contact_number:
        errors['contact_number'] = 'Contact number is required.'
    elif not PHONE_REGEX.match(contact_number):
        errors['contact_number'] = 'Contact number must be exactly 11 digits (0-9).'

    if email:
        if len(email) > 150:
            errors['email'] = 'Email must be at most 150 characters.'
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = 'Enter a valid email address.'

    if not company_name:
        errors['company_name'] = 'Company is required.'
    elif len(company_name) > 150:
        errors['company_name'] = 'Company name must be at most 150 characters.'

    if not contact_name:
        errors['contact_name'] = 'Contact person is required.'
    elif len(contact_name) > 150:
        errors['contact_name'] = 'Contact person must be at most 150 characters.'

    if not purpose_name:
        errors['purpose_name'] = 'Purpose is required.'
    elif len(purpose_name) > 150:
        errors['purpose_name'] = 'Purpose must be at most 150 characters.'

    cleaned_data = {
        'lastname': lastname,
        'firstname': firstname,
        'middle_initial': middle_initial or None,
        'suffix': suffix or None,
        'contact_number': contact_number,
        'email': email or None,
        'company_name': company_name,
        'contact_name': contact_name,
        'purpose_name': purpose_name,
    }

    return cleaned_data, errors