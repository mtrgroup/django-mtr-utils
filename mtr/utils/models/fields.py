from django.db import models


class ManyFields:

    # TODO: make more compact

    def __new__(cls, _field, *fields_and_labels, **params):
        class ManyFieldsMixin(models.Model):

            class Meta:
                abstract = True

        for field, label in fields_and_labels:
            params['verbose_name'] = label

            ManyFieldsMixin.add_to_class(field, _field(**params))

        return ManyFieldsMixin
