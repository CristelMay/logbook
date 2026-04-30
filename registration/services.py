from django.db import connection, transaction
from django.utils import timezone
from zoneinfo import ZoneInfo


MANILA_TZ = ZoneInfo('Asia/Manila')


def _current_manila_naive_datetime():
	"""Return the current Manila time as a naive datetime for TIMESTAMP columns."""
	return timezone.localtime(timezone.now(), MANILA_TZ).replace(tzinfo=None)


def create_guest_visit(cleaned_data):
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO guest (
                    lastname,
                    firstname,
                    middle_initial,
                    suffix,
                    contact_number,
                    email
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING guest_id;
                """,
                [
                    cleaned_data['lastname'],
                    cleaned_data['firstname'],
                    cleaned_data['middle_initial'],
                    cleaned_data['suffix'],
                    cleaned_data['contact_number'],
                    cleaned_data['email'],
                ],
            )
            guest_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO visitor_company (company_name)
                VALUES (%s)
                RETURNING company_id;
                """,
                [cleaned_data['company_name']],
            )
            company_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO employee (full_name)
                VALUES (%s)
                RETURNING contact_id;
                """,
                [cleaned_data['contact_name']],
            )
            contact_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO visit_purpose (purpose_name)
                VALUES (%s)
                RETURNING purpose_id;
                """,
                [cleaned_data['purpose_name']],
            )
            purpose_id = cursor.fetchone()[0]

            current_manila_time = _current_manila_naive_datetime()
            cursor.execute(
                """
                INSERT INTO visit_log (
                    date_of_visit,
                    time_in,
                    guest_id,
                    company_id,
                    contact_id,
                    purpose_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING visit_id;
                """,
                [
                    current_manila_time.date(),
                    current_manila_time,
                    guest_id,
                    company_id,
                    contact_id,
                    purpose_id,
                ],
            )
            row = cursor.fetchone()
            return row[0] if row else None