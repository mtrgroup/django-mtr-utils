from functools import wraps

from django.conf import settings
from django.shortcuts import redirect


def anonymous_required(f):
    """Redirect authorized user to his cabinet"""

    # TODO: func to check where user should be redirected

    @wraps(f)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(request.GET.get(
                'next', getattr(settings, 'DEFAULT_AUTH_URL', '/')))
        return f(request, *args, **kwargs)
    return inner
