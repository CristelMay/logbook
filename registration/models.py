from django.db import models

# Create your models here.

from django.db import connection


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