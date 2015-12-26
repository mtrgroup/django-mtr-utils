from setuptools import setup, find_packages

import os

from mtr.utils import VERSION, get_version


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.md')

version_tuple = VERSION
version = get_version()

setup(
    name='django-mtr-utils',
    packages=find_packages(exclude=('tests/', 'docs/')),
    version=version,
    author='mtr group',
    author_email='inboxmtr@gmail.com',
    url='https://github.com/mtrgroup/django-mtr-utils',
    description=README,
    long_description=README,
    namespace_packages=('mtr',),
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords=['django', 'helpers', 'mixins', 'shortcuts'],
    install_requires=['Django>=1.6'],
)
