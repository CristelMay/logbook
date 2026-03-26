from django.db import connection, transaction


def create_guest_visit(cleaned_data):
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT create_guest_visit(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """,
                [
                    cleaned_data['lastname'],
                    cleaned_data['firstname'],
                    cleaned_data['middle_initial'],
                    cleaned_data['suffix'],
                    cleaned_data['contact_number'],
                    cleaned_data['email'],
                    cleaned_data['company_name'],
                    cleaned_data['contact_name'],
                    cleaned_data['purpose_name'],
                ],
            )
            row = cursor.fetchone()
            return row[0] if row else None