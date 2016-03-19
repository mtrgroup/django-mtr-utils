from django import forms

from .widgets import SelectizeCategoryWidget


class GlobalInitialFormMixin(object):

    """Class initial params for instance initial kwarg"""

    INITIAL = {}

    def __init__(self, *args, **kwargs):
        if kwargs.get('initial', None):
            kwargs['initial'].update(self.INITIAL)
        super(GlobalInitialFormMixin, self).__init__(*args, **kwargs)


class SelectizeCategoryFormMixin(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        params = {}

        if self.instance is not None:
            params['group_id'] = self.instance.group_id

        self.fields['linked_to'] = forms.ModelChoiceField(
            label=self.fields['linked_to'].label,
            required=self.fields['linked_to'].required,
            queryset=self.Meta.model.objects.all(),
            widget=SelectizeCategoryWidget(self.Meta.model, params=params))
