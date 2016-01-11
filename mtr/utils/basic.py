import re


def lreplace(pattern, sub, string):
    """Replaces 'pattern' in 'string' with 'sub'
    if 'pattern' starts 'string'."""

    return re.sub('^%s' % pattern, sub, string)
