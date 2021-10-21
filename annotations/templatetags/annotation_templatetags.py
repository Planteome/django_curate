from django import template

# models import
from ..models import Annotation

register = template.Library()


@register.simple_tag
def get_annotation(key):
    return Annotation.objects.get(pk=key)
