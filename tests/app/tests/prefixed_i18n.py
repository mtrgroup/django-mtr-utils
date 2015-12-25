# coding: utf-8
from __future__ import unicode_literals

import os
import functools

from django.test import SimpleTestCase
from django.utils import translation
from django.utils.safestring import mark_safe
from django.template.engine import Engine
from django.template import Library
from django.template.base import libraries
from django.utils._os import upath
from django.test.utils import override_settings

ROOT = os.path.dirname(os.path.abspath(upath(__file__)))
TEMPLATE_DIR = os.path.join(ROOT, 'templates')


def setup(templates, *args, **kwargs):
    """
    Runs test method multiple times in the following order:
    debug       cached      string_if_invalid
    -----       ------      -----------------
    False       False
    False       True
    False       False       INVALID
    False       True        INVALID
    True        False
    True        True
    """
    # when testing deprecation warnings, it's useful to run just one test since
    # the message won't be displayed multiple times
    test_once = kwargs.get('test_once', False)

    for arg in args:
        templates.update(arg)

    # numerous tests make use of an inclusion tag
    # add this in here for simplicity
    templates["inclusion.html"] = "{{ result }}"

    loaders = [
        ('django.template.loaders.cached.Loader', [
            ('django.template.loaders.locmem.Loader', templates),
        ]),
    ]

    def decorator(func):
        @register_test_tags
        # Make Engine.get_default() raise an exception to ensure that tests
        # are properly isolated from Django's global settings.
        @override_settings(TEMPLATES=None)
        @functools.wraps(func)
        def inner(self):
            self.engine = Engine(
                allowed_include_roots=[ROOT],
                loaders=loaders,
            )
            func(self)
            if test_once:
                return
            func(self)

            self.engine = Engine(
                allowed_include_roots=[ROOT],
                loaders=loaders,
                string_if_invalid='INVALID',
            )
            func(self)
            func(self)

            self.engine = Engine(
                allowed_include_roots=[ROOT],
                debug=True,
                loaders=loaders,
            )
            func(self)
            func(self)

        return inner

    return decorator


register = Library()


def register_test_tags(func):
    @functools.wraps(func)
    def inner(self):
        libraries['testtags'] = register
        try:
            func(self)
        finally:
            del libraries['testtags']
    return inner


class I18nTagTests(SimpleTestCase):
    libraries = {
        'i18n': 'mtr.templatetags.prefixed_i18n',
    }

    @setup({'i18n01': '{% load i18n %}{% trans \'xxxyyyxxx\' %}'})
    def test_i18n01(self):
        """
        simple translation of a string delimited by '
        """
        output = self.engine.render_to_string('i18n01')
        self.assertEqual(output, 'xxxyyyxxx')

    @setup({'i18n02': '{% load i18n %}{% trans "xxxyyyxxx" %}'})
    def test_i18n02(self):
        """
        simple translation of a string delimited by "
        """
        output = self.engine.render_to_string('i18n02')
        self.assertEqual(output, 'xxxyyyxxx')

    @setup({'i18n03': '{% load i18n %}{% blocktrans %}{{ anton }}{% endblocktrans %}'})
    def test_i18n03(self):
        """
        simple translation of a variable
        """
        output = self.engine.render_to_string('i18n03', {'anton': b'\xc3\x85'})
        self.assertEqual(output, 'Å')

    @setup({'i18n04': '{% load i18n %}{% blocktrans with berta=anton|lower %}{{ berta }}{% endblocktrans %}'})
    def test_i18n04(self):
        """
        simple translation of a variable and filter
        """
        output = self.engine.render_to_string('i18n04', {'anton': b'\xc3\x85'})
        self.assertEqual(output, 'å')

    @setup({'legacyi18n04': '{% load i18n %}'
                            '{% blocktrans with anton|lower as berta %}{{ berta }}{% endblocktrans %}'})
    def test_legacyi18n04(self):
        """
        simple translation of a variable and filter
        """
        output = self.engine.render_to_string('legacyi18n04', {'anton': b'\xc3\x85'})
        self.assertEqual(output, 'å')

    @setup({'i18n05': '{% load i18n %}{% blocktrans %}xxx{{ anton }}xxx{% endblocktrans %}'})
    def test_i18n05(self):
        """
        simple translation of a string with interpolation
        """
        output = self.engine.render_to_string('i18n05', {'anton': 'yyy'})
        self.assertEqual(output, 'xxxyyyxxx')

    @setup({'i18n06': '{% load i18n %}{% trans "Page not found" %}'})
    def test_i18n06(self):
        """
        simple translation of a string to german
        """
        with translation.override('de'):
            output = self.engine.render_to_string('i18n06')
        self.assertEqual(output, 'Seite nicht gefunden')

    @setup({'i18n07': '{% load i18n %}'
                      '{% blocktrans count counter=number %}singular{% plural %}'
                      '{{ counter }} plural{% endblocktrans %}'})
    def test_i18n07(self):
        """
        translation of singular form
        """
        output = self.engine.render_to_string('i18n07', {'number': 1})
        self.assertEqual(output, 'singular')

    @setup({'legacyi18n07': '{% load i18n %}'
                            '{% blocktrans count number as counter %}singular{% plural %}'
                            '{{ counter }} plural{% endblocktrans %}'})
    def test_legacyi18n07(self):
        """
        translation of singular form
        """
        output = self.engine.render_to_string('legacyi18n07', {'number': 1})
        self.assertEqual(output, 'singular')

    @setup({'i18n08': '{% load i18n %}'
                      '{% blocktrans count number as counter %}singular{% plural %}'
                      '{{ counter }} plural{% endblocktrans %}'})
    def test_i18n08(self):
        """
        translation of plural form
        """
        output = self.engine.render_to_string('i18n08', {'number': 2})
        self.assertEqual(output, '2 plural')

    @setup({'legacyi18n08': '{% load i18n %}'
                            '{% blocktrans count counter=number %}singular{% plural %}'
                            '{{ counter }} plural{% endblocktrans %}'})
    def test_legacyi18n08(self):
        """
        translation of plural form
        """
        output = self.engine.render_to_string('legacyi18n08', {'number': 2})
        self.assertEqual(output, '2 plural')

    @setup({'i18n09': '{% load i18n %}{% trans "Page not found" noop %}'})
    def test_i18n09(self):
        """
        simple non-translation (only marking) of a string to german
        """
        with translation.override('de'):
            output = self.engine.render_to_string('i18n09')
        self.assertEqual(output, 'Page not found')

    @setup({'i18n10': '{{ bool|yesno:_("yes,no,maybe") }}'})
    def test_i18n10(self):
        """
        translation of a variable with a translated filter
        """
        with translation.override('de'):
            output = self.engine.render_to_string('i18n10', {'bool': True})
        self.assertEqual(output, 'Ja')

    @setup({'i18n11': '{{ bool|yesno:"ja,nein" }}'})
    def test_i18n11(self):
        """
        translation of a variable with a non-translated filter
        """
        output = self.engine.render_to_string('i18n11', {'bool': True})
        self.assertEqual(output, 'ja')

    @setup({'i18n12': '{% load i18n %}'
                      '{% get_available_languages as langs %}{% for lang in langs %}'
                      '{% if lang.0 == "de" %}{{ lang.0 }}{% endif %}{% endfor %}'})
    def test_i18n12(self):
        """
        usage of the get_available_languages tag
        """
        output = self.engine.render_to_string('i18n12')
        self.assertEqual(output, 'de')

    @setup({'i18n13': '{{ _("Password") }}'})
    def test_i18n13(self):
        """
        translation of constant strings
        """
        with translation.override('de'):
            output = self.engine.render_to_string('i18n13')
        self.assertEqual(output, 'Passwort')

    @setup({'i18n14': '{% cycle "foo" _("Password") _(\'Password\') as c %} {% cycle c %} {% cycle c %}'})
    def test_i18n14(self):
        """
        translation of constant strings
        """
        with translation.override('de'):
            output = self.engine.render_to_string('i18n14')
        self.assertEqual(output, 'foo Passwort Passwort')

    @setup({'i18n15': '{{ absent|default:_("Password") }}'})
    def test_i18n15(self):
        """
        translation of constant strings
        """
        with translation.override('de'):
            output = self.engine.render_to_string('i18n15', {'absent': ''})
        self.assertEqual(output, 'Passwort')

    @setup({'i18n16': '{{ _("<") }}'})
    def test_i18n16(self):
        """
        translation of constant strings
        """
        with translation.override('de'):
            output = self.engine.render_to_string('i18n16')
        self.assertEqual(output, '<')

    @setup({'i18n17': '{% load i18n %}'
                      '{% blocktrans with berta=anton|escape %}{{ berta }}{% endblocktrans %}'})
    def test_i18n17(self):
        """
        Escaping inside blocktrans and trans works as if it was directly in the template.
        """
        output = self.engine.render_to_string('i18n17', {'anton': 'α & β'})
        self.assertEqual(output, 'α &amp; β')

    @setup({'i18n18': '{% load i18n %}'
                      '{% blocktrans with berta=anton|force_escape %}{{ berta }}{% endblocktrans %}'})
    def test_i18n18(self):
        output = self.engine.render_to_string('i18n18', {'anton': 'α & β'})
        self.assertEqual(output, 'α &amp; β')

    @setup({'i18n19': '{% load i18n %}{% blocktrans %}{{ andrew }}{% endblocktrans %}'})
    def test_i18n19(self):
        output = self.engine.render_to_string('i18n19', {'andrew': 'a & b'})
        self.assertEqual(output, 'a &amp; b')

    @setup({'i18n20': '{% load i18n %}{% trans andrew %}'})
    def test_i18n20(self):
        output = self.engine.render_to_string('i18n20', {'andrew': 'a & b'})
        self.assertEqual(output, 'a &amp; b')

    @setup({'i18n21': '{% load i18n %}{% blocktrans %}{{ andrew }}{% endblocktrans %}'})
    def test_i18n21(self):
        output = self.engine.render_to_string('i18n21', {'andrew': mark_safe('a & b')})
        self.assertEqual(output, 'a & b')

    @setup({'i18n22': '{% load i18n %}{% trans andrew %}'})
    def test_i18n22(self):
        output = self.engine.render_to_string('i18n22', {'andrew': mark_safe('a & b')})
        self.assertEqual(output, 'a & b')

    @setup({'legacyi18n17': '{% load i18n %}'
                            '{% blocktrans with anton|escape as berta %}{{ berta }}{% endblocktrans %}'})
    def test_legacyi18n17(self):
        output = self.engine.render_to_string('legacyi18n17', {'anton': 'α & β'})
        self.assertEqual(output, 'α &amp; β')

    @setup({'legacyi18n18': '{% load i18n %}'
                            '{% blocktrans with anton|force_escape as berta %}'
                            '{{ berta }}{% endblocktrans %}'})
    def test_legacyi18n18(self):
        output = self.engine.render_to_string('legacyi18n18', {'anton': 'α & β'})
        self.assertEqual(output, 'α &amp; β')

    @setup({'i18n23': '{% load i18n %}{% trans "Page not found"|capfirst|slice:"6:" %}'})
    def test_i18n23(self):
        """
        #5972 - Use filters with the {% trans %} tag
        """
        with translation.override('de'):
            output = self.engine.render_to_string('i18n23')
        self.assertEqual(output, 'nicht gefunden')

    @setup({'i18n24': '{% load i18n %}{% trans \'Page not found\'|upper %}'})
    def test_i18n24(self):
        with translation.override('de'):
            output = self.engine.render_to_string('i18n24')
        self.assertEqual(output, 'SEITE NICHT GEFUNDEN')

    @setup({'i18n25': '{% load i18n %}{% trans somevar|upper %}'})
    def test_i18n25(self):
        with translation.override('de'):
            output = self.engine.render_to_string('i18n25', {'somevar': 'Page not found'})
        self.assertEqual(output, 'SEITE NICHT GEFUNDEN')

    @setup({'i18n26': '{% load i18n %}'
                      '{% blocktrans with extra_field=myextra_field count counter=number %}'
                      'singular {{ extra_field }}{% plural %}plural{% endblocktrans %}'})
    def test_i18n26(self):
        """
        translation of plural form with extra field in singular form (#13568)
        """
        output = self.engine.render_to_string('i18n26', {'myextra_field': 'test', 'number': 1})
        self.assertEqual(output, 'singular test')

    @setup({'legacyi18n26': '{% load i18n %}'
                            '{% blocktrans with myextra_field as extra_field count number as counter %}'
                            'singular {{ extra_field }}{% plural %}plural{% endblocktrans %}'})
    def test_legacyi18n26(self):
        output = self.engine.render_to_string('legacyi18n26', {'myextra_field': 'test', 'number': 1})
        self.assertEqual(output, 'singular test')

    @setup({'i18n27': '{% load i18n %}{% blocktrans count counter=number %}'
                      '{{ counter }} result{% plural %}{{ counter }} results'
                      '{% endblocktrans %}'})
    def test_i18n27(self):
        """
        translation of singular form in russian (#14126)
        """
        with translation.override('ru'):
            output = self.engine.render_to_string('i18n27', {'number': 1})
        self.assertEqual(output, '1 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442')

    @setup({'legacyi18n27': '{% load i18n %}'
                            '{% blocktrans count number as counter %}{{ counter }} result'
                            '{% plural %}{{ counter }} results{% endblocktrans %}'})
    def test_legacyi18n27(self):
        with translation.override('ru'):
            output = self.engine.render_to_string('legacyi18n27', {'number': 1})
        self.assertEqual(output, '1 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442')

    @setup({'i18n28': '{% load i18n %}'
                      '{% blocktrans with a=anton b=berta %}{{ a }} + {{ b }}{% endblocktrans %}'})
    def test_i18n28(self):
        """
        simple translation of multiple variables
        """
        output = self.engine.render_to_string('i18n28', {'anton': 'α', 'berta': 'β'})
        self.assertEqual(output, 'α + β')

    @setup({'legacyi18n28': '{% load i18n %}'
                            '{% blocktrans with anton as a and berta as b %}'
                            '{{ a }} + {{ b }}{% endblocktrans %}'})
    def test_legacyi18n28(self):
        output = self.engine.render_to_string('legacyi18n28', {'anton': 'α', 'berta': 'β'})
        self.assertEqual(output, 'α + β')

    # retrieving language information
    @setup({'i18n28_2': '{% load i18n %}'
                        '{% get_language_info for "de" as l %}'
                        '{{ l.code }}: {{ l.name }}/{{ l.name_local }} bidi={{ l.bidi }}'})
    def test_i18n28_2(self):
        output = self.engine.render_to_string('i18n28_2')
        self.assertEqual(output, 'de: German/Deutsch bidi=False')

    @setup({'i18n29': '{% load i18n %}'
                      '{% get_language_info for LANGUAGE_CODE as l %}'
                      '{{ l.code }}: {{ l.name }}/{{ l.name_local }} bidi={{ l.bidi }}'})
    def test_i18n29(self):
        output = self.engine.render_to_string('i18n29', {'LANGUAGE_CODE': 'fi'})
        self.assertEqual(output, 'fi: Finnish/suomi bidi=False')

    @setup({'i18n30': '{% load i18n %}'
                      '{% get_language_info_list for langcodes as langs %}'
                      '{% for l in langs %}{{ l.code }}: {{ l.name }}/'
                      '{{ l.name_local }} bidi={{ l.bidi }}; {% endfor %}'})
    def test_i18n30(self):
        output = self.engine.render_to_string('i18n30', {'langcodes': ['it', 'no']})
        self.assertEqual(output, 'it: Italian/italiano bidi=False; no: Norwegian/norsk bidi=False; ')

    @setup({'i18n31': '{% load i18n %}'
                      '{% get_language_info_list for langcodes as langs %}'
                      '{% for l in langs %}{{ l.code }}: {{ l.name }}/'
                      '{{ l.name_local }} bidi={{ l.bidi }}; {% endfor %}'})
    def test_i18n31(self):
        output = self.engine.render_to_string('i18n31', {'langcodes': (('sl', 'Slovenian'), ('fa', 'Persian'))})
        self.assertEqual(
            output,
            'sl: Slovenian/Sloven\u0161\u010dina bidi=False; '
            'fa: Persian/\u0641\u0627\u0631\u0633\u06cc bidi=True; '
        )

    # blocktrans handling of variables which are not in the context.
    # this should work as if blocktrans was not there (#19915)
    @setup({'i18n34': '{% load i18n %}{% blocktrans %}{{ missing }}{% endblocktrans %}'})
    def test_i18n34(self):
        output = self.engine.render_to_string('i18n34')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, '')

    @setup({'i18n34_2': '{% load i18n %}{% blocktrans with a=\'α\' %}{{ missing }}{% endblocktrans %}'})
    def test_i18n34_2(self):
        output = self.engine.render_to_string('i18n34_2')
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, '')

    @setup({'i18n34_3': '{% load i18n %}{% blocktrans with a=anton %}{{ missing }}{% endblocktrans %}'})
    def test_i18n34_3(self):
        output = self.engine.render_to_string('i18n34_3', {'anton': '\xce\xb1'})
        if self.engine.string_if_invalid:
            self.assertEqual(output, 'INVALID')
        else:
            self.assertEqual(output, '')

    # trans tag with as var
    @setup({'i18n35': '{% load i18n %}{% trans "Page not found" as page_not_found %}{{ page_not_found }}'})
    def test_i18n35(self):
        with translation.override('de'):
            output = self.engine.render_to_string('i18n35')
        self.assertEqual(output, 'Seite nicht gefunden')

    @setup({'i18n36': '{% load i18n %}'
                      '{% trans "Page not found" noop as page_not_found %}{{ page_not_found }}'})
    def test_i18n36(self):
        with translation.override('de'):
            output = self.engine.render_to_string('i18n36')
        self.assertEqual(output, 'Page not found')

    @setup({
        'i18n37': '{% load i18n %}'
            '{% trans "Page not found" as page_not_found %}'
            '{% blocktrans %}Error: {{ page_not_found }}{% endblocktrans %}'
        })
    def test_i18n37(self):
        with translation.override('de'):
            output = self.engine.render_to_string('i18n37')
        self.assertEqual(output, 'Error: Seite nicht gefunden')
