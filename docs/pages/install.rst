============
Installation
============

.. contents::
   :depth: 3

Stable version
==============

Not-yet released :(

Development version
===================

Use one pip command to install package::

   pip install git+https://github.com/mtrgroup/django-mtr-utils.git#egg=django-mtr-utils

You can get it the latest source from our `git`_ repository::

   git clone git://github.com/mtrgroup/django-mtr-utils.git django-mtr-utils

Add the resulting folder to your `PYTHONPATH`_ or symlink the ``mtr`` directory
inside it into a directory which is on your PYTHONPATH, such as your Python
installation's ``site-packages`` directory.

You can verify that the application is available on your PYTHONPATH by
opening a Python interpreter and entering the following commands::

   >>> import mtr.utils
   >>> mtr.utils.VERSION
   (0, 1)

When you want to update your copy of the source code, run ``git pull``
from within the ``django-mtr-utils`` directory.

.. caution::

   The development version may contain bugs which are not present in the
   release version and introduce backwards-incompatible changes.

   If you're tracking master, keep an eye on the recent `Commit History`_
   before you update your copy of the source code.

.. _`git`: http://git-scm.com/
.. _`PYTHONPATH`: http://docs.python.org/tut/node8.html#SECTION008110000000000000000
.. _`Commit History`: http://github.com/mtrgroup/django-mtr-utils/commits/master
