default_app_config = 'mtr.utils.apps.MtrUtilsConfig'

VERSION = (0, 1)


def get_version():
    return '.'.join(str(v) for v in VERSION)
