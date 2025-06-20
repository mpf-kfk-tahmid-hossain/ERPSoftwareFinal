# ERPSoftwareFinal

This project is a sample ERP system implemented with Django. It demonstrates multi-tenant onboarding, role based permissions, and custom HTMX forms for interaction.

## Password Hashing

Passwords are stored using the Argon2 hashing algorithm for improved security. Ensure `argon2-cffi` is installed when deploying.
This project requires Pillow for profile picture uploads.

Uploaded media files are stored in the `media/` directory during development. Ensure `MEDIA_ROOT` and `MEDIA_URL` are configured and that Django serves media files when `DEBUG=True`.
