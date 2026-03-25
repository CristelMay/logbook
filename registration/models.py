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
