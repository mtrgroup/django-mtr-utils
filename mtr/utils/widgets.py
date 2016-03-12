from django import forms
from django.core.urlresolvers import reverse

from .helpers import model_app_name
from .translation import _


class RelatedModelWidget(forms.widgets.Widget):

    class Media:
        js = ('admin/js/relatedmodel.js',)

    def __init__(self, model, attrs=None, auto_add=False):
        self.model = model
        self.auto_add = auto_add

        super().__init__(attrs)

    # TODO: refactor
    def render(self, name, value, attrs=None):
        model_label = reverse(
            'utils:model_label', args=(model_app_name(self.model), value))
        list_url = '{}?_popup=1'.format(
            reverse('admin:{}_{}_changelist'.format(
                self.model._meta.app_label,
                self.model._meta.object_name.lower())))
        edit_url = '{}?_popup=1'.format(
            reverse('admin:{}_{}_change'.format(
                self.model._meta.app_label,
                self.model._meta.object_name.lower()), args=(value,)))

        if self.auto_add:
            action = 'data-model-autoadd'
            action_label = _('Add')
        else:
            action = 'data-model-choose'
            action_label = _('Choose')

        return '<div data-model-info="{}"></div>' \
            '<input id="id_{}" name="{}" type="hidden" value="{}">' \
            '<a href="{}" {}>' \
            '{}</a>&nbsp;<a href="{}" data-model-edit>' \
            '{}</a>'.format(
                model_label, name, name, value,
                list_url, action,
                action_label, edit_url, _('Edit'))
