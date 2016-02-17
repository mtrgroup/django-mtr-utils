from django.db import models

from ..translation import _


class ManyFields(object):

    def __new__(cls, _field, *fields_and_labels, **params):
        class ManyFieldsMixin(models.Model):

            class Meta:
                abstract = True

        for field, label in fields_and_labels:
            params['verbose_name'] = label

            ManyFieldsMixin.add_to_class(field, _field(**params))

        return ManyFieldsMixin


class ManyFieldsAuto(object):
    _ = _

    def __new__(cls, _field, *fields, **newparams):
        labels = map(lambda f: f.replace('_', ' '), fields)
        params = {}
        params.update(newparams)

        class ManyFieldsAutoMixin(models.Model):

            class Meta:
                abstract = True

        for field, label in zip(fields, labels):
            params['verbose_name'] = label

            ManyFieldsAutoMixin.add_to_class(field, _field(**params))

        return ManyFieldsAutoMixin
