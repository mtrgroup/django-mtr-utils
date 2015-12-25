import math

from django import template
from django.conf import settings
from django.utils.formats import get_format
from django.utils.translation import get_language

from ..helpers import chunks as chunks_helper

register = template.Library()

@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.simple_tag
def settings_format(name):
    lang = get_language()
    return get_format(name, lang, use_l10n=settings.USE_L10N)


@register.simple_tag
def format_get_values(request, name, key):
    GET = request.GET.copy()
    key = str(key)
    value = GET.get(name, None)

    if value is not None and key in value:
        value = ','.join(filter(lambda v: key != v, value.split(',')))
    else:
        value = value.split(',') if value else []
        value = ','.join(value + [key])

    if value:
        GET[name] = value
    else:
        GET.pop(name, None)
    params = GET.urlencode()

    return '{}?{}'.format(request.path, params)


@register.simple_tag
def request_path_replace(request, key, value=None):
    GET = request.GET.copy()
    if value:
        GET[key] = value
    else:
        GET.pop(key, None)
    GET.pop('page', None)
    params = GET.urlencode()
    return '{}?{}'.format(request.path, params)


@register.filter
def split(string, separator):
    return string.split(separator)


@register.filter
def substract(md, sd):
    return md - sd


@register.filter
def get(item, key):
    return item.get(key, None)


@register.filter
def in_group(user, group):
    return group in list(map(lambda g: g.name, user.groups.all()))


@register.filter
def chunks(l, m):
    if l is None:
        return l
    return chunks_helper(l, m)


@register.filter
def chunks_by(l, m):
    if l is None:
        return l
    if len(l) < 6:
        return [l]
    return chunks_helper(l, math.ceil(len(l) / m))
