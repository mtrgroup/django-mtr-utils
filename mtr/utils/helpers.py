import os
import types
import collections

from functools import wraps

import django

from django.db import models
from django.conf import settings
from django.utils.encoding import smart_text
from django.shortcuts import render
from django.utils.six.moves import filterfalse, range
from django.utils.six.moves.urllib.parse import urljoin
from django.core.exceptions import PermissionDenied

from .settings import THEMES, DOMAIN_URL

# TODO: separate to smaller libs


def themed_path(
        template, version_subdirectory=False,
        base_dir=THEMES['base_dir'],
        theme=THEMES['theme']):
    """Changing template themes by setting THEME_PATH and django version"""

    path = os.path.join(base_dir, theme)

    if version_subdirectory:
        path = os.path.join(path, django.get_version()[:3])

    return os.path.join(path, template)


def render_to(template, *args, **kwargs):
    """Shortuct for rendering templates,
    creates functions that returns decorator for view"""

    decorator_kwargs = kwargs

    # TODO: add check if file exist if not try use base theme
    # if base not found use fall back, then raise error with original
    # template provided in function

    # outer decorator
    def decorator(f):

        # inner decorator
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            response = f(request, *args, **kwargs)
            if isinstance(response, dict):
                new_template = template
                if decorator_kwargs.pop(
                        'themed', THEMES['use_in_render']):
                    new_template = themed_path(template)

                return render(
                    request, new_template,
                    response, **decorator_kwargs)
            else:
                return response
        return wrapper

    return decorator


def make_prefixed_themed_path(prefix):
    """Shortcut for prefixing template dir path"""

    def inner(template, version_subdirectory=False):
        return themed_path(
            os.path.join(prefix, template),
            version_subdirectory=version_subdirectory)

    return inner


def make_prefixed_render_to(prefix):
    """Shortcut for prefixing template dir render"""

    def inner(template, *args, **kwargs):
        return render_to(
            os.path.join(prefix, template), *args, **kwargs)

    return inner


def chunks(l, n, as_list=False):
    """Chunk list by n slices and return iterator or list"""

    n = max(1, n)
    iterator = [l[i:i + n] for i in range(0, len(l), n)]
    return list(iterator) if as_list else iterator


def update_nested_dict(d, u):
    """Simple function to update nested dict"""

    # TODO: needs more tests in some cases updates all dict instead of values

    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update_nested_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def make_from_params(model, params):
    """Create model instance from dict or get by id from database"""

    if params.get('id', None):
        return model.objects.get(id=params['id'])
    return model(**params)


def model_settings(model, name):
    """Get specific settings from model"""

    return getattr(getattr(model, 'Settings', {}), name, {})


def in_group_plain(user, name):
    """Check user name if listed in groups"""

    return name in list(map(lambda g: g.name, user.groups.all()))


def in_group(name):
    """Check if user in group and run view func or raise PermissionDenied"""

    def decorator(f):

        @wraps(f)
        def wrapper(request, *args, **kwargs):
            if in_group_plain(request.user, name):
                return f(request, *args, **kwargs)
            else:
                raise PermissionDenied

        return wrapper

    return decorator


def update_instance(instance, attrs):
    """Updates instance with given attrs dict"""

    for key, value in attrs.items():
        setattr(instance, key, value)
    instance.save()

    return instance


def find_dublicates(model, fields):
    """Find all dublicate instances and returns queryset"""

    duplicates = model.objects.values(fields).order_by() \
        .annotate(max_id=models.Max('id'), count_id=models.Count('id')) \
        .filter(count_id__gt=1)
    return model.objects.filter(id__in=map(lambda d: d['max_id'], duplicates))


def absolute_url(path):
    """Return url with domain in settings for inner functions"""

    return urljoin(DOMAIN_URL, path.lstrip('/'))


def relative_media_url(path):
    """Return url with domain in settings for inner functions"""

    return urljoin(settings.MEDIA_URL, path.lstrip('/'))


def models_list():
    """Return all registered models"""

    from django.apps import apps

    mlist = apps.get_models()
    mlist = (m for m in mlist
             if model_settings(m, 'sync').get('ignore', False))

    return mlist


def model_app_name(model):
    return '{}.{}'.format(
        model._meta.app_label, model._meta.object_name.lower())


def model_choices(empty=True):
    """Return all registered django models as choices"""

    if empty:
        yield ('', '-' * 9)

    for model in models_list():
        yield (
            model_app_name(model),
            smart_text('{} | {}').format(
                model._meta.app_label.title(),
                model._meta.verbose_name.title()))


class MethodWrapper(object):
    """
    Used for exposing private and long methods to simple class with
    public human readable names. For example using them in django templates
    """

    def __init__(self, instance, bind=None):
        self.instance = instance
        self.bind = bind or []

        for template, names in bind:
            for name in names:
                self._bind_method(template.format(name), name)

    def _bind_method(self, m_from, m_to):
        def func(self, *args, **kwargs):
            return getattr(self.instance, m_from)(*args, **kwargs)

        setattr(self, m_to, types.MethodType(func, self))
