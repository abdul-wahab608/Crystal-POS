"""
Core views for health check and system monitoring
"""
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import sys


def health_check(request):
    """
    Health check endpoint for desktop app
    Returns system status, database connectivity, and Python info
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JsonResponse({
        "status": "healthy",
        "database": db_status,
        "python_version": sys.version,
        "django_version": settings.DATABASES['default']['ENGINE'],
        "debug": settings.DEBUG
    })
