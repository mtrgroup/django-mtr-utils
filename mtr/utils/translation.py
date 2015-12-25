from django.utils.translation import gettext_lazy, gettext

from .settings import GETTEXT


def make_prefixed_string(func, makeprefix, makeformat=None):
    """Shortcut for prefixing (formating) string passed to function"""

    makeformat = makeformat or GETTEXT['FORMAT']

    def inner(string, prefix=None, cformat=None):
        """String prefixed before passed in func"""

        prefix = prefix or makeprefix
        cformat = cformat or makeformat

        return func(cformat.format(prefix, string))
    return inner


def make_prefixed_gettext_lazy(makeprefix, makeformat=None):
    """Shortcut for gettext_lazy pre-formating"""

    return make_prefixed_string(
        gettext_lazy, makeprefix, makeformat=makeformat)


def make_prefixed_gettext(makeprefix, makeformat=None):
    """Shortcut for gettext pre-formating"""

    return make_prefixed_string(
        gettext, makeprefix, makeformat=makeformat)

_ = make_prefixed_gettext_lazy('mtr.utils')
