from __future__ import unicode_literals

import sys

from django.templatetags.i18n import TemplateSyntaxError, Variable, Node, \
    render_value_in_context, TOKEN_TEXT, TOKEN_VAR
from django.template import Library
from django.template.defaulttags import token_kwargs
from django.utils import six, translation

from ..settings import GETTEXT

register = Library()


class TranslateNode(Node):

    def __init__(self, filter_expression, noop, asvar=None,
                 message_context=None):
        self.noop = noop
        self.asvar = asvar
        self.message_context = message_context
        self.filter_expression = filter_expression
        if isinstance(self.filter_expression.var, six.string_types):
            self.filter_expression.var = Variable(
                "'%s'" % self.filter_expression.var)
        self.request = Variable('request')

    def render(self, context):
        i18n_prefix = self.request.resolve(context).resolver_match.app_name
        i18n_prefix = context.get('__i18n_prefix', i18n_prefix)
        self.filter_expression.var.literal = GETTEXT['format'].format(
            i18n_prefix, self.filter_expression.var.literal)
        self.filter_expression.var.translate = not self.noop
        if self.message_context:
            self.filter_expression.var.message_context = (
                self.message_context.resolve(context))

        output = self.filter_expression.resolve(context)

        value = render_value_in_context(output, context)

        if self.asvar:
            context[self.asvar] = value
            return ''
        else:
            return value


@register.tag("trans")
def do_translate(parser, token):
    """
    This will mark a string for translation and will
    translate the string for the current language.
    Usage::
        {% trans "this is a test" %}
    This will mark the string for translation so it will
    be pulled out by mark-messages.py into the .po files
    and will run the string through the translation engine.
    There is a second form::
        {% trans "this is a test" noop %}
    This will only mark for translation, but will return
    the string unchanged. Use it when you need to store
    values into forms that should be translated later on.
    You can use variables instead of constant strings
    to translate stuff you marked somewhere else::
        {% trans variable %}
    This will just try to translate the contents of
    the variable ``variable``. Make sure that the string
    in there is something that is in the .po file.
    It is possible to store the translated string into a variable::
        {% trans "this is a test" as var %}
        {{ var }}
    Contextual translations are also supported::
        {% trans "this is a test" context "greeting" %}
    This is equivalent to calling pgettext instead of (u)gettext.
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument" % bits[0])
    message_string = parser.compile_filter(bits[1])
    remaining = bits[2:]

    noop = False
    asvar = None
    message_context = None
    seen = set()
    invalid_context = {'as', 'noop'}

    while remaining:
        option = remaining.pop(0)
        if option in seen:
            raise TemplateSyntaxError(
                "The '%s' option was specified more than once." % option,
            )
        elif option == 'noop':
            noop = True
        elif option == 'context':
            try:
                value = remaining.pop(0)
            except IndexError:
                msg = "No argument provided to the " \
                    "'%s' tag for the context option." % bits[0]
                six.reraise(
                    TemplateSyntaxError, TemplateSyntaxError(msg),
                    sys.exc_info()[2])
            if value in invalid_context:
                raise TemplateSyntaxError(
                    "Invalid argument '%s' provided to the"
                    " '%s' tag for the context option" % (value, bits[0]),
                )
            message_context = parser.compile_filter(value)
        elif option == 'as':
            try:
                value = remaining.pop(0)
            except IndexError:
                msg = "No argument provided to the '%s' tag for " \
                    "the as option." % bits[0]
                six.reraise(
                    TemplateSyntaxError, TemplateSyntaxError(msg),
                    sys.exc_info()[2])
            asvar = value
        else:
            raise TemplateSyntaxError(
                "Unknown argument for '%s' tag: '%s'. The only options "
                "available are 'noop', 'context' \"xxx\", and 'as VAR'." % (
                    bits[0], option,
                )
            )
        seen.add(option)

    return TranslateNode(message_string, noop, asvar, message_context)


class BlockTranslateNode(Node):

    def __init__(
            self, extra_context, singular, plural=None, countervar=None,
            counter=None, message_context=None, trimmed=False, asvar=None):
        self.extra_context = extra_context
        self.singular = singular
        self.plural = plural
        self.countervar = countervar
        self.counter = counter
        self.message_context = message_context
        self.trimmed = trimmed
        self.asvar = asvar
        self.request = Variable('request')

    def render_token_list(self, tokens):
        result = []
        vars = []
        for token in tokens:
            if token.token_type == TOKEN_TEXT:
                result.append(token.contents.replace('%', '%%'))
            elif token.token_type == TOKEN_VAR:
                result.append('%%(%s)s' % token.contents)
                vars.append(token.contents)
        msg = ''.join(result)
        if self.trimmed:
            msg = translation.trim_whitespace(msg)
        return msg, vars

    def render(self, context, nested=False):
        if self.message_context:
            message_context = self.message_context.resolve(context)
        else:
            message_context = None
        tmp_context = {}
        for var, val in self.extra_context.items():
            tmp_context[var] = val.resolve(context)
        # Update() works like a push(), so corresponding context.pop() is at
        # the end of function
        context.update(tmp_context)
        singular, vars = self.render_token_list(self.singular)
        i18n_prefix = self.request.resolve(context).resolver_match.app_name
        i18n_prefix = context.get('__i18n_prefix', i18n_prefix)
        singular = GETTEXT['format'].format(i18n_prefix, singular)
        if self.plural and self.countervar and self.counter:
            count = self.counter.resolve(context)
            context[self.countervar] = count
            plural, plural_vars = self.render_token_list(self.plural)
            if message_context:
                result = translation.npgettext(message_context, singular,
                                               plural, count)
            else:
                result = translation.ungettext(singular, plural, count)
            vars.extend(plural_vars)
        else:
            if message_context:
                result = translation.pgettext(message_context, singular)
            else:
                result = translation.ugettext(singular)
        default_value = context.template.engine.string_if_invalid

        def render_value(key):
            if key in context:
                val = context[key]
            else:
                val = default_value % key \
                    if '%s' in default_value else default_value
            return render_value_in_context(val, context)

        data = {v: render_value(v) for v in vars}
        context.pop()
        try:
            result = result % data
        except (KeyError, ValueError):
            if nested:
                # Either string is malformed, or it's a bug
                raise TemplateSyntaxError(
                    "'blocktrans' is unable to format "
                    "string returned by gettext: %r "
                    "using %r" % (result, data))
            with translation.override(None):
                result = self.render(context, nested=True)
        if self.asvar:
            context[self.asvar] = result
            return ''
        else:
            return result


@register.tag("blocktrans")
def do_block_translate(parser, token):
    """
    This will translate a block of text with parameters.
    Usage::
        {% blocktrans with bar=foo|filter boo=baz|filter %}
        This is {{ bar }} and {{ boo }}.
        {% endblocktrans %}
    Additionally, this supports pluralization::
        {% blocktrans count count=var|length %}
        There is {{ count }} object.
        {% plural %}
        There are {{ count }} objects.
        {% endblocktrans %}
    This is much like ngettext, only in template syntax.
    The "var as value" legacy format is still supported::
        {% blocktrans with foo|filter as bar and baz|filter as boo %}
        {% blocktrans count var|length as count %}
    The translated string can be stored in a variable using `asvar`::
        {% blocktrans with bar=foo|filter boo=baz|filter asvar var %}
        This is {{ bar }} and {{ boo }}.
        {% endblocktrans %}
        {{ var }}
    Contextual translations are supported::
        {% blocktrans with bar=foo|filter context "greeting" %}
            This is {{ bar }}.
        {% endblocktrans %}
    This is equivalent to calling pgettext/npgettext instead of
    (u)gettext/(u)ngettext.
    """
    bits = token.split_contents()

    options = {}
    remaining_bits = bits[1:]
    asvar = None
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise TemplateSyntaxError('The %r option was specified more '
                                      'than once.' % option)
        if option == 'with':
            value = token_kwargs(remaining_bits, parser, support_legacy=True)
            if not value:
                raise TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % bits[0])
        elif option == 'count':
            value = token_kwargs(remaining_bits, parser, support_legacy=True)
            if len(value) != 1:
                raise TemplateSyntaxError('"count" in %r tag expected exactly '
                                          'one keyword argument.' % bits[0])
        elif option == "context":
            try:
                value = remaining_bits.pop(0)
                value = parser.compile_filter(value)
            except Exception:
                msg = (
                    '"context" in %r tag expected '
                    'exactly one argument.') % bits[0]
                six.reraise(
                    TemplateSyntaxError, TemplateSyntaxError(msg),
                    sys.exc_info()[2])
        elif option == "trimmed":
            value = True
        elif option == "asvar":
            try:
                value = remaining_bits.pop(0)
            except IndexError:
                msg = "No argument provided to the '%s' tag for the" \
                    " asvar option." % bits[0]
                six.reraise(
                    TemplateSyntaxError, TemplateSyntaxError(msg),
                    sys.exc_info()[2])
            asvar = value
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (bits[0], option))
        options[option] = value

    if 'count' in options:
        countervar, counter = list(options['count'].items())[0]
    else:
        countervar, counter = None, None
    if 'context' in options:
        message_context = options['context']
    else:
        message_context = None
    extra_context = options.get('with', {})

    trimmed = options.get("trimmed", False)

    singular = []
    plural = []
    while parser.tokens:
        token = parser.next_token()
        if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
            singular.append(token)
        else:
            break
    if countervar and counter:
        if token.contents.strip() != 'plural':
            raise TemplateSyntaxError(
                "'blocktrans' doesn't allow other block tags inside it")
        while parser.tokens:
            token = parser.next_token()
            if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
                plural.append(token)
            else:
                break
    if token.contents.strip() != 'endblocktrans':
        raise TemplateSyntaxError(
            "'blocktrans' doesn't allow other block tags (seen %r) "
            "inside it" % token.contents)

    return BlockTranslateNode(extra_context, singular, plural, countervar,
                              counter, message_context, trimmed=trimmed,
                              asvar=asvar)


@register.simple_tag(takes_context=True)
def set_i18n_prefix(context, name):
    context['__i18n_prefix'] = name
    return ''
