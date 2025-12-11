"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import FileResponse, Http404
from .views import health_check
import os


def serve_vue_app(request):
    """Serve Vue.js SPA index.html for all non-API routes"""
    install_dir = os.environ.get('CRYSTAL_INSTALL_DIR')
    
    possible_dirs = []
    if install_dir:
        possible_dirs.append(os.path.join(install_dir, 'frontend', 'dist'))
    possible_dirs.append(os.path.join(settings.BASE_DIR.parent, 'frontend', 'dist'))
    possible_dirs.append(os.path.join(str(settings.BASE_DIR.parent), 'frontend', 'dist'))
    
    for frontend_dir in possible_dirs:
        index_path = os.path.join(frontend_dir, 'index.html')
        index_path = os.path.normpath(index_path)
        if os.path.exists(index_path):
            return FileResponse(open(index_path, 'rb'), content_type='text/html')
    
    raise Http404("Frontend not found. Please check installation.")


def serve_static_file(request, path):
    """Serve static files from Vue dist folder"""
    # Handle both installed (Program Files) and development paths
    install_dir = os.environ.get('CRYSTAL_INSTALL_DIR')
    
    # Try multiple possible frontend locations
    possible_dirs = []
    
    if install_dir:
        possible_dirs.append(os.path.join(install_dir, 'frontend', 'dist'))
    
    # Standard paths relative to backend
    possible_dirs.append(os.path.join(settings.BASE_DIR.parent, 'frontend', 'dist'))
    possible_dirs.append(os.path.join(settings.BASE_DIR, '..', 'frontend', 'dist'))
    
    # For Program Files installation: BASE_DIR is 'backend', parent is install root
    possible_dirs.append(os.path.join(str(settings.BASE_DIR.parent), 'frontend', 'dist'))
    
    for frontend_dir in possible_dirs:
        file_path = os.path.join(frontend_dir, path)
        # Normalize path to handle any path traversal
        file_path = os.path.normpath(file_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            content_types = {
                '.js': 'application/javascript',
                '.css': 'text/css',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon',
                '.woff': 'font/woff',
                '.woff2': 'font/woff2',
                '.ttf': 'font/ttf',
                '.json': 'application/json',
            }
            ext = os.path.splitext(path)[1].lower()
            content_type = content_types.get(ext, 'application/octet-stream')
            return FileResponse(open(file_path, 'rb'), content_type=content_type)
    
    # Log what was tried (for debugging)
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Static file not found: {path}")
    logger.warning(f"Tried directories: {possible_dirs}")
    
    raise Http404(f"Static file not found: {path}")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    # API endpoints - fixed to match frontend expectations
    path('api/users/', include('users.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/vendors/', include('vendors.urls')),
    path('api/products/', include('products.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/purchases/', include('purchases.urls')),
    path('api/assets/', include('assets.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/raw-materials/', include('raw_materials.urls')),
    path('api/bank-accounts/', include('bank_accounts.urls')),
]

# Serve Vue frontend in production (when dist folder exists)
FRONTEND_DIR = os.path.join(settings.BASE_DIR.parent, 'frontend', 'dist')
if os.path.exists(FRONTEND_DIR):
    urlpatterns += [
        # Serve favicon
        re_path(r'^favicon\.ico$', serve_static_file, {'path': 'favicon.ico'}),
        # Serve static assets (JS, CSS, images, fonts) - prepend 'assets/' to path
        re_path(r'^assets/(?P<path>.*)$', lambda request, path: serve_static_file(request, f'assets/{path}')),
        re_path(r'^(?P<path>.*\.(js|css|png|jpg|jpeg|svg|ico|woff|woff2|ttf|json))$', serve_static_file),
        # Catch-all for Vue SPA routing - must be last
        re_path(r'^(?!api/|admin/).*$', serve_vue_app, name='vue_app'),
    ]
