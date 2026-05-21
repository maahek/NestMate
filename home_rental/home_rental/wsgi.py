"""
NestMate — WSGI Configuration

Used by traditional web servers like Gunicorn in production.

Run in production:
    gunicorn home_rental.wsgi:application --bind 0.0.0.0:8000

Note: For WebSocket (chat feature), use asgi.py + Daphne instead.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_rental.settings')

application = get_wsgi_application()