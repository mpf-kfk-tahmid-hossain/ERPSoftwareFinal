"""
WSGI config for erp_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Ensure the full settings path is used so importing works during tests.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_project.erp_project.settings')

application = get_wsgi_application()
