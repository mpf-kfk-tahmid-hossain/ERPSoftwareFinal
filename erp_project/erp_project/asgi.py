"""
ASGI config for erp_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Ensure the full settings path is used so importing works during tests.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_project.erp_project.settings')

application = get_asgi_application()
