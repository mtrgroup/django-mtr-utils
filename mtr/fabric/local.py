import os
import sys

import django

from fabric.api import local, task, lcd, settings, env
from babel.messages.pofile import read_po, write_po

from mtr.utils.basic import lreplace


@task
def clear():
    """Delete unnecessary and cached files"""

    local(
        "find . -name '~*' -or -name '*.pyo' -or -name '*.pyc' "
        "-or -name '__pycache__' -or -name 'Thubms.db' "
        "| xargs -I {} rm -vrf '{}'")


@task
def subl():
    """Start Sublime editor"""

    local('subl project.sublime-project')


@task
def docs(action='build'):
    """Sphinx docs generation"""

    with lcd(env.vars['docs']):
        if action == 'build':
            local('make html')
        elif action == 'update':
            local('rm -f mtr*')
            local('sphinx-apidoc -o . ../mtr/')
        else:
            print(
                'Invalid action: {}, available actions: "make"'
                ', "update"'.format(action))


@task
def install():
    """Install packages for testing"""

    with lcd(env.vars['project']['dir']):
        local('pip install -r requirements/python{}.txt'.format(
            sys.version_info[0]))


@task
def manage(command, coverage=None):
    """Shortcut for manage.py file"""

    run = './manage.py {}'

    if coverage:
        run = '{} {}'.format(coverage, run)

    with lcd(env.vars['project']['dir']):
        local(run.format(command))

        if coverage:
            local('mv .coverage ../')


@task
def test(coverage=False):
    """Test listed apps"""

    apps = []
    apps.extend(env.vars['project']['apps'])
    apps.extend(env.vars['apps'])
    test_apps = ' '.join(map(lambda app: '{}.tests'.format(app), apps))
    command = "test {} --pattern='*.py'".format(test_apps)

    if coverage:
        coverage = "coverage run --omit=*.virtualenvs/*," \
            "*migrations/*.py,*tests*,*/admin.py," \
            "*templatetags/*.py,*utils/*.py"

    manage(command, coverage)


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

    with lcd(env.vars['project']['dir']):
        local('celery worker -A app')


@task
def locale(action='make', lang='en'):
    """Make messages, and compile messages for listed apps"""

    if action == 'make':
        for app in env.vars['apps']:
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
        for app in env.vars['apps']:
            app_path = os.path.join(*app.split('.'))

            with lcd(app_path), settings(warn_only=True):
                local('django-admin.py compilemessages -l {}'.format(lang))
    else:
        print(
            'Invalid action: {}, available actions: "make"'
            ', "compile"'.format(action))


@task
def migrate():
    """Simple data migration management"""

    if django.get_version() >= '1.7':
        manage('makemigrations')
    else:
        for app in env.vars['apps'] + env.vars['project']['apps']:
            manage('schemamigration --initial {}'.format(app.split('.')[-1]))
        manage('syncdb --noinput')

    manage('migrate')


@task
def recreate(username='app', password='app'):
    """Recreate new migrations from start and remove database"""

    project_prefixed_apps = []
    for app in env.vars['project']['apps']:
        project_prefixed_apps.append('{}.{}'.format(
            env.vars['project']['dir'], app))

    apps = env.vars['apps'] + project_prefixed_apps

    for app in apps:
        with lcd(os.path.join(*app.split('.'))), settings(warn_only=True):
            if django.get_version() >= '1.7':
                local('rm -f ./migrations/*.py')
                local('touch ./migrations/__init__.py')
            else:
                local('rm -f ./south_migrations/*.py')
                local('touch ./south_migrations/__init__.py')
    with lcd(env.vars['project']['dir']):
        if django.get_version() >= '1.7':
            local('rm -f db.sqlite3')
        else:
            local('rm -rf olddb.sqlite3')

    migrate()

    manage('createsuperuser --username app --email app@app.com --noinput')
    manage('changepassword app')
