import json

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


# REFACTOR: for all selectboxes
class SelectizeCategoryWidget(forms.widgets.Widget):

    class Media:
        js = (
            'mtr/utils/vendor/selectize/js/selectize.min.js',
            'mtr/utils/widgets/selectize.js'
        )
        css = {
            'screen': ('mtr/utils/vendor/selectize/css/selectize.suit.css',)
        }

    def __init__(self, model, attrs=None, params=None):
        self.params = params or {}
        self.model = model

        super().__init__(attrs)

    def render(self, name, value, attrs=None):
        # TODO: use django rest framework

        resource = reverse('utils:model_resource', args=(
            model_app_name(self.model),))
        params = json.dumps(self.params)
        option = ''
        if value:
            item = self.model.objects.get(id=value)
            option = '<option name="{}">{}</option>'.format(
                value, item.get_name_path())

        return """
            <div class="selectize-widget">
            <select id="id_{0}" name="{0}" value="{1}"
                data-selectize-select="{2}"
                data-params='{3}'
                placeholder="Введите категорию...">
                {4}
            </select></div>""".format(name, value, resource, params, option)
