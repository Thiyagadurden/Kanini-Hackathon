from rest_framework import permissions

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'patient'

class IsNurse(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'nurse'

class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'doctor'

class IsManagement(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'management'

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsPatientOrNurseOrDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['patient', 'nurse', 'doctor']

class IsDoctorOrNurse(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['doctor', 'nurse']

class IsAdminOrManagement(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'management']

class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'doctor', 'nurse']:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'patient'):
            return obj.patient.user == request.user
        return False

class ReadOnlyForManagement(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'management':
            return request.method in permissions.SAFE_METHODS
        return request.user.role in ['admin', 'doctor', 'nurse']
