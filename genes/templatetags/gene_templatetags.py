from django import template

# models import
from ..models import Gene

register = template.Library()


@register.simple_tag
def get_gene(key):
    return Gene.objects.get(pk=key)
