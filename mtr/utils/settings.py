from django.conf import settings


def strip_media_root(path):
    if path:
        return path.split(settings.MEDIA_ROOT.rstrip('/'))[1].lstrip('/')
    return path


def getattr_with_prefix(prefix, name, default):
    """Custom settings prefix for avoiding name colissions"""

    prefix = getattr(settings, '{}_SETTINGS_PREFIX'.format(prefix), prefix)

    default.update(getattr(settings, '{}_{}'.format(prefix, name), {}))

    return default

SETTINGS = getattr_with_prefix('UTILS', 'SETTINGS', {
    'template': {
        'apps': [],
        'default_apps': True,
    },
    'gettext': {
        'format': '{}:{}',
    },
    'themes': {
        'dir': 'themes',
        'theme': 'default',
        'use_in_render': True,
        'fallback_to_default': True
    },
    'domain': 'http://localhost/'
})
