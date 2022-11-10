from django import template

# models import
from ..models import Gene

# choices import
import curate.choices as choices

register = template.Library()


@register.simple_tag
def get_gene(key):
    return Gene.objects.get(pk=key)

@register.simple_tag
def get_aspect(key):
    aspectChoices=choices.AspectCode
    for choice in aspectChoices:
        if key == choice.value:
            return choice.name


@register.simple_tag
def get_evCode(key):
    evCodeChoices=choices.EvidenceCode
    for choice in evCodeChoices:
        if key == choice.value:
            return choice.name