# django-mtr-utils

## Helper package, with don't repeat yourself ideology

### Inlcudes Model mixins, helpers, shortcuts, pagination classes, decorators

[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/mtrgroup/django-mtr-utils/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/mtrgroup/django-mtr-utils/?branch=master) [![Code Coverage](https://scrutinizer-ci.com/g/mtrgroup/django-mtr-utils/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/mtrgroup/django-mtr-utils/?branch=master) [![Build Status](https://scrutinizer-ci.com/g/mtrgroup/django-mtr-utils/badges/build.png?b=master)](https://scrutinizer-ci.com/g/mtrgroup/django-mtr-utils/build-status/master) [![Documentation Status](https://readthedocs.org/projects/django-mtr-utils/badge/?version=latest)](https://readthedocs.org/projects/django-mtr-utils/?badge=latest)

Project updates here [http://mtr.website](http://mtr.website)


## Documentation
Includes only docstrings from module [http://django-mtr-utils.rtfd.org/](http://django-mtr-utils.rtfd.org/)

## How to use
1. Install package:
   `pip install git+https://github.com/mtrgroup/django-mtr-utils.git`
2. Add `mtr.utils` to `INSTALLED_APPS` in your settings file for templatetags
3. Migrate models `./manage.py migrate`

## Features
- Gettext prefixed strings
- Supports: Django 1.6-1.9+ Python 2.7, 3.3+

## Working on
- Documentation
- Tests
- Rewrite paginator without 3-rd party lib

