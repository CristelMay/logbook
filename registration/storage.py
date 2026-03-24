import os
import uuid

from supabase import create_client


def _get_client_and_bucket():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    bucket_name = os.getenv('SUPABASE_BUCKET', 'profile-pictures')

    if not supabase_url or not supabase_key:
        raise ValueError('Supabase credentials are not configured.')

    return create_client(supabase_url, supabase_key), bucket_name


def upload_profile_image(file_bytes, original_name, content_type):
    client, bucket_name = _get_client_and_bucket()

    extension = ''
    if '.' in original_name:
        extension = original_name.rsplit('.', 1)[1].lower()

    file_name = f"guards/{uuid.uuid4().hex}"
    if extension:
        file_name = f"{file_name}.{extension}"

    client.storage.from_(bucket_name).upload(
        path=file_name,
        file=file_bytes,
        file_options={
            'content-type': content_type,
            'upsert': 'false',
        },
    )

    return file_name


def get_profile_image_url(storage_path):
    if not storage_path:
        return ''

    # Keep backward compatibility in case older rows still have full URLs.
    if str(storage_path).startswith('http://') or str(storage_path).startswith('https://'):
        return storage_path

    client, bucket_name = _get_client_and_bucket()
    expires_in = int(os.getenv('SUPABASE_SIGNED_SECONDS', '300'))

    signed = client.storage.from_(bucket_name).create_signed_url(storage_path, expires_in)
    return signed.get('signedURL') or signed.get('signedUrl') or ''
