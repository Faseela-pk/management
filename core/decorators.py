from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role == 'Admin' or request.user.is_superuser):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

def staff_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role in ['Admin', 'Staff'] or request.user.is_superuser):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

def student_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ['Admin', 'Staff', 'Student']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
