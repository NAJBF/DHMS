from rest_framework import permissions

class IsStudent(permissions.BasePermission):
    """
    Allows access only to authenticated users with 'student' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'student')


class IsProctor(permissions.BasePermission):
    """
    Allows access only to authenticated users with 'proctor' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'proctor')


class IsStaffMember(permissions.BasePermission):
    """
    Allows access only to authenticated users with 'staff' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'staff')


class IsSecurity(permissions.BasePermission):
    """
    Allows access only to authenticated users with 'security' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'security')


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to authenticated users with 'admin' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser))
