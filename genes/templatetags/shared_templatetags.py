from django import template

from django.utils.safestring import mark_safe

# difflib import
import difflib

register = template.Library()

# Note that this is templatetags that are to be shared across apps, but because of
# Django restrictions, must live in an app.


@register.simple_tag
def inline_diff(a, b):
    matcher = difflib.SequenceMatcher(None, a, b)

    def process_tag(tag, i1, i2, j1, j2):
        if tag == 'replace':
            return '<span style="color:red">' + matcher.a[i1:i2] + '</span><span style="color:green">' + matcher.b[
                                                                                                         j1:j2] + '</span>'
        if tag == 'delete':
            return '<span style="color:red">' + matcher.a[i1:i2] + '</span>'
        if tag == 'equal':
            return matcher.a[i1:i2]
        if tag == 'insert':
            return '<span style="color:green">' + matcher.b[j1:j2] + '</span>'
        assert False, "Unknown tag %r" % tag

    return mark_safe(''.join(process_tag(*t) for t in matcher.get_opcodes()))


@register.filter
def pipe_space(string):
    return string.replace('|', ' | ')
