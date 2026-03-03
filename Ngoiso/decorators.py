from django.shortcuts import redirect
from functools import wraps

def superuser_or_usertype(allowed_types=[]):
    """
    Decorator to allow access if:
    - User is superuser
    - OR user.user_type is in allowed_types
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if user.is_authenticated and (user.is_superuser or user.user_type in allowed_types):
                return view_func(request, *args, **kwargs)
            else:
                return redirect('error_page')  # or a custom access denied page
        return _wrapped_view
    return decorator