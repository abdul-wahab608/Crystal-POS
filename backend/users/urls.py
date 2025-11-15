from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, login_view, current_user_view, logout_view

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', login_view, name='login'),
    path('auth/me/', current_user_view, name='current_user'),
    path('auth/logout/', logout_view, name='logout'),
    # User management endpoints
    path('', include(router.urls)),
] 