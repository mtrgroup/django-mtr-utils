class GlobalInitialFormMixin(object):

    """Class initial params for instance initial kwarg"""

    INITIAL = {}

    def __init__(self, *args, **kwargs):
        if kwargs.get('initial', None):
            kwargs['initial'].update(self.INITIAL)
        super(GlobalInitialFormMixin, self).__init__(*args, **kwargs)
