from unittest import TestCase

from django.db import models

from mtr.utils.models.fields import ManyFields
from mtr.utils.translation import _


class ManyFieldsTest(TestCase):

    # def setUp(self):
        # self.manager = Base

    def test_char_fields(self):
        CharFieldsMixin = ManyFields(
            models.CharField, ('name', _('name')))

        for field in CharFieldsMixin._meta.fields:
            self.assertIsInstance(field, models.CharField)
            self.assertEqual(field.name, 'name')
