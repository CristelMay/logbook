from django.db import models

# Create your models here.

from django.db import connection
from django.utils import timezone
from zoneinfo import ZoneInfo


MANILA_TZ = ZoneInfo('Asia/Manila')


def username_exists(username):
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT 1
			FROM users
			WHERE lower(username) = lower(%s)
			LIMIT 1;
			""",
			[username],
		)
		return cursor.fetchone() is not None


def view_all_guards():
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT user_id, username, full_name, profile_pic, is_active
			FROM view_all_guards();
			"""
		)
		rows = cursor.fetchall()

	guards = []
	for user_id, username, full_name, profile_pic, is_active in rows:
		guards.append(
			{
				'user_id': user_id,
				'username': username,
				'full_name': full_name,
				'profile_pic': profile_pic,
				'is_active': is_active,
			}
		)

	return guards


def get_guard_info(user_id):
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT user_id, username, full_name, profile_pic
			FROM get_guard_info(%s);
			""",
			[user_id],
		)
		row = cursor.fetchone()

	if not row:
		return None

	guard_user_id, username, full_name, profile_pic = row
	return {
		'user_id': guard_user_id,
		'username': username,
		'full_name': full_name,
		'profile_pic': profile_pic,
	}


def reset_user_password(user_id, new_password):
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT reset_user_password(%s, %s);
			""",
			[user_id, new_password],
		)
		row = cursor.fetchone()

	return row[0] if row else None


def get_user_profile(user_id):
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT u.user_id, u.username, p.firstname, p.lastname, p.middle_initial, p.suffix
			FROM users u
			JOIN person p ON u.person_id = p.person_id
			WHERE u.user_id = %s;
			""",
			[user_id],
		)
		row = cursor.fetchone()

	if not row:
		return None

	return {
		'user_id': row[0],
		'username': row[1],
		'first_name': row[2] or '',
		'last_name': row[3] or '',
		'middle_initial': row[4] or '',
		'suffix': row[5] or '',
	}


def update_user_profile(user_id, username, last_name, first_name, middle_initial, suffix, profile_pic=None):
	with connection.cursor() as cursor:
		if profile_pic is not None:
			cursor.execute(
				"""
				UPDATE users SET username = %s, profile_pic = %s WHERE user_id = %s;
				UPDATE person p SET firstname = %s, lastname = %s, middle_initial = %s, suffix = %s
				FROM users u WHERE u.person_id = p.person_id AND u.user_id = %s;
				""",
				[username, profile_pic, user_id, first_name, last_name, middle_initial, suffix, user_id],
			)
		else:
			cursor.execute(
				"""
				UPDATE users SET username = %s WHERE user_id = %s;
				UPDATE person p SET firstname = %s, lastname = %s, middle_initial = %s, suffix = %s
				FROM users u WHERE u.person_id = p.person_id AND u.user_id = %s;
				""",
				[username, user_id, first_name, last_name, middle_initial, suffix, user_id],
			)


def create_user_account(
	username,
	password,
	role_id,
	last_name,
	first_name,
	middle_initial,
	suffix,
	profile_pic,
):
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT create_user_account(%s, %s, %s, %s, %s, %s, %s, %s);
			""",
			[
				username,
				password,
				role_id,
				last_name,
				first_name,
				middle_initial,
				suffix,
				profile_pic,
			],
		)
		row = cursor.fetchone()

	return row[0] if row else None


def get_guest_logs():
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT visit_id, guest_name, contact_number, company_name, contact_person,
			       purpose_name, guard_name, date_of_visit, time_in, time_out, status
			FROM view_guest_logs();
			"""
		)
		rows = cursor.fetchall()

	guest_logs = []
	for visit_id, guest_name, contact_number, company_name, contact_person, purpose_name, guard_name, date_of_visit, time_in, time_out, status in rows:
		guest_logs.append({
			'visit_id': visit_id,
			'guest_name': guest_name,
			'contact_number': contact_number,
			'company_name': company_name,
			'contact_person': contact_person,
			'purpose_name': purpose_name,
			'guard_name': guard_name or '—',
			'date_raw': date_of_visit.strftime('%Y-%m-%d') if date_of_visit else '',
			'date_of_visit': date_of_visit.strftime('%b %d, %Y') if date_of_visit else '',
			'time_in': time_in.strftime('%I:%M %p') if time_in else '',
			'time_out': time_out.strftime('%I:%M %p') if time_out else '—',
			'status': status,
		})

	return guest_logs

def checkout_visit(visit_id):
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			UPDATE visit_log
			SET time_out = CURRENT_TIMESTAMP
			WHERE visit_id = %s;
			""",
			[visit_id],
		)


def get_active_visitors():
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT visit_id, guest_name, company_name, purpose_name, contact_person, time_in
			FROM view_guest_logs()
			WHERE status = 'Checked In'
			AND date_of_visit = CURRENT_DATE;
			"""
		)
		rows = cursor.fetchall()

	active_visitors = []
	for visit_id, guest_name, company_name, purpose_name, contact_person, time_in in rows:
		active_visitors.append({
			'visit_id': visit_id,
			'guest_name': guest_name,
			'company_name': company_name,
			'purpose_name': purpose_name,
			'contact_person': contact_person,
			'time_in': time_in.strftime('%I:%M %p') if time_in else '',
		})

	return active_visitors


def get_dashboard_stats():
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT total_today, currently_inside, checked_out_today, total_this_month
			FROM get_dashboard_stats();
			"""
		)
		row = cursor.fetchone()

	if not row:
		return {
			'total_today': 0,
			'currently_inside': 0,
			'checked_out_today': 0,
			'total_this_month': 0,
		}

	total_today, currently_inside, checked_out_today, total_this_month = row
	return {
		'total_today': total_today,
		'currently_inside': currently_inside,
		'checked_out_today': checked_out_today,
		'total_this_month': total_this_month,
	}


def get_recent_checkouts():
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT guest_name, company_name, time_in, time_out, duration
			FROM get_recent_checkouts();
			"""
		)
		rows = cursor.fetchall()

	def _format_manila_time(value):
		if not value:
			return ''

		if not hasattr(value, 'strftime'):
			return str(value)

		datetime_value = value
		if timezone.is_naive(datetime_value):
			datetime_value = timezone.make_aware(datetime_value, timezone=ZoneInfo('UTC'))

		datetime_value = timezone.localtime(datetime_value, MANILA_TZ)
		return datetime_value.strftime('%I:%M %p')

	recent_checkouts = []
	for guest_name, company_name, time_in, time_out, duration in rows:
		time_in_display = _format_manila_time(time_in)
		time_out_display = _format_manila_time(time_out)
		recent_checkouts.append(
			{
				'guest_name': guest_name,
				'company_name': company_name,
				'time_in': time_in_display,
				'time_out': time_out_display,
				'duration': duration,
			}
		)

	return recent_checkouts


def get_frequent_visitors():
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT guest_name, company_name, total_visits
			FROM get_frequent_visitors();
			"""
		)
		rows = cursor.fetchall()

	frequent_visitors = []
	for guest_name, company_name, total_visits in rows:
		frequent_visitors.append(
			{
				'guest_name': guest_name,
				'company_name': company_name,
				'total_visits': total_visits,
			}
		)

	return frequent_visitors


def get_today_visitor_log():
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT guest_name, company_name, purpose_name, contact_number, contact_person, time_in, time_out
			FROM get_today_visitor_log();
			"""
		)
		rows = cursor.fetchall()

	today_visitor_log = []
	for guest_name, company_name, purpose_name, contact_number, contact_person, time_in, time_out in rows:
		today_visitor_log.append(
			{
				'guest_name': guest_name,
				'company_name': company_name,
				'purpose_name': purpose_name,
				'contact_number': contact_number,
				'contact_person': contact_person,
				'time_in': time_in,
				'time_out': time_out,
			}
		)

	return today_visitor_log