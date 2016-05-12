from __future__ import unicode_literals

from django.apps import AppConfig
from .translation import gettext_lazy as _


class MtrUtilsConfig(AppConfig):
    name = 'mtr.utils'
    label = 'mtr_utils'
    verbose_name = _('Utilities')
