from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()

class IsManagerUser(permissions.BasePermission):
    """Allow access to admin and manager users."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager()

class IsCashierUser(permissions.BasePermission):
    """Allow access to admin, manager, and cashier users."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_cashier()

class IsStaffUser(permissions.BasePermission):
    """Allow access to all authenticated users."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated 