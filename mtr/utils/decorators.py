from functools import wraps

from django.conf import settings
from django.shortcuts import redirect


def anonymous_required(
        f, redirect_to=getattr(settings, 'DEFAULT_AUTH_URL', '/')):
    """Redirect authorized user to his cabinet"""

    @wraps(f)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(redirect_to)
        return f(request, *args, **kwargs)
    return inner
