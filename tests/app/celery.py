from __future__ import absolute_import

import os
import sys

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# insert parent dir to path
# sys.path.insert(
    # 0, os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))

app = Celery('app')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
