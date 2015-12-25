import os
import sys
import re

import django

from fabric.api import local, task, lcd, settings
from babel.messages.pofile import read_po, write_po

APPS = []
PROJECT_APPS = ['app']
PROJECT_DIR = 'tests'
DOCS_DIR = 'docs'


def lreplace(pattern, sub, string):
    """Replaces 'pattern' in 'string' with 'sub'
    if 'pattern' starts 'string'."""

    return re.sub('^%s' % pattern, sub, string)


@task
def clear():
    """Delete unnecessary and cached files"""

    local(
        "find . -name '~*' -or -name '*.pyo' -or -name '*.pyc' "
        "-or -name '__pycache__' -or -name 'Thubms.db' "
        "| xargs -I {} rm -vrf '{}'")


@task
def manage(command, prefix=None, nocd=False):
    """Shortcut for manage.py file"""

    run = '{}/manage.py {{}}'.format(PROJECT_DIR if nocd else '.')

    if prefix:
        run = '{} {}'.format(prefix, run)

    if nocd:
        local(run.format(command))
    else:
        with lcd(PROJECT_DIR):
            local(run.format(command))


@task
def test(coverage=False):
    """Test listed apps"""

    if django.get_version() >= '1.7':
        apps = []
        apps.extend(PROJECT_APPS)
        apps.extend(APPS)
        test_apps = ' '.join(map(lambda app: '{}.tests'.format(app), apps))
        command = "test {} --pattern='*.py'".format(test_apps)
    else:
        command = "test --pattern='*.py'"

    if coverage:
        coverage = "coverage run --omit=*.virtualenvs/*," \
            "*migrations/*.py,*tests*,*/admin.py," \
            "*templatetags/*.py"

    manage(command, prefix=coverage, nocd=coverage)


@task
def run():
    """Run server"""

    manage('runserver')


@task
def shell():
    """Start interactive shell"""

    manage('shell')


@task
def celery():
    """Start celery worker"""

    with lcd(PROJECT_DIR):
        local('celery worker -A app')


@task
def locale(action='make', lang='en'):
    """Make messages, and compile messages for listed apps"""

    if action == 'make':
        for app in APPS:
            app_path = os.path.join(*app.split('.'))

            with lcd(app_path):
                po_path = os.path.join(
                    app_path, 'locale', lang, 'LC_MESSAGES', 'django.po')
                if not os.path.exists(po_path):
                    local('django-admin.py makemessages -l {}'.format(lang))
                with open(po_path, 'rb') as f:
                    catalog = read_po(f)
                    for message in catalog:
                        message.id = lreplace(
                            '{}:'.format(app), '', message.id)
                with open(po_path, 'wb') as f:
                    write_po(f, catalog, include_previous=True)
                local('django-admin.py makemessages -l {}'.format(lang))
                with open(po_path, 'rb') as f:
                    catalog = read_po(f)
                    for message in catalog:
                        if lang == 'en':
                            message.string = str(message.id)
                        else:
                            if not message.string:
                                message.string = str(message.id)
                        message.id = '{}:{}'.format(app, message.id)
                with open(po_path, 'wb') as f:
                    write_po(f, catalog, include_previous=True)
    elif action == 'compile':
        for app in APPS:
            app_path = os.path.join(*app.split('.'))

            with lcd(app_path), settings(warn_only=True):
                local('django-admin.py compilemessages -l {}'.format(lang))
    else:
        print(
            'Invalid action: {}, available actions: "make"'
            ', "compile"'.format(action))


@task
def install():
    """Install packages for testing"""

    with lcd(PROJECT_DIR):
        local('pip install -r requirements/python{}.txt'.format(
            sys.version_info[0]))


@task
def migrate():
    """Simple data migration management"""

    if django.get_version() >= '1.7':
        manage('makemigrations')
    else:
        for app in APPS + PROJECT_APPS:
            manage('schemamigration --initial {}'.format(app.split('.')[-1]))
        manage('syncdb --noinput')

    manage('migrate')


@task
def recreate(username='app', password='app'):
    """Recreate new migrations from start and remove database"""

    project_prefixed_apps = []
    for app in PROJECT_APPS:
        project_prefixed_apps.append('{}.{}'.format(PROJECT_DIR, app))

    apps = APPS + project_prefixed_apps

    for app in apps:
        with lcd(os.path.join(*app.split('.'))), settings(warn_only=True):
            if django.get_version() >= '1.7':
                local('rm -f ./migrations/*.py')
                local('touch ./migrations/__init__.py')
            else:
                local('rm -f ./south_migrations/*.py')
                local('touch ./south_migrations/__init__.py')
    with lcd(PROJECT_DIR):
        if django.get_version() >= '1.7':
            local('rm -f db.sqlite3')
        else:
            local('rm -rf olddb.sqlite3')

    migrate()

    manage('createsuperuser --username app --email app@app.com --noinput')
    manage('changepassword app')


@task
def subl():
    """Start Sublime editor"""

    local('subl project.sublime-project')


@task
def docs(action='make'):
    """Sphinx docs generation"""

    with lcd(DOCS_DIR):
        if action == 'build':
            local('make html')
        elif action == 'update':
            local('rm -f mtr*')
            local('sphinx-apidoc -o . ../mtr/')
        else:
            print(
                'Invalid action: {}, available actions: "make"'
                ', "update"'.format(action))
