from __future__ import unicode_literals

import django


if django.get_version() >= '1.7':
    from django.apps import AppConfig
    from .translation import gettext_lazy as _

    class MtrUtilsConfig(AppConfig):
        name = 'mtr.utils'
        label = 'mtr_utils'
        verbose_name = _('Utilities')
