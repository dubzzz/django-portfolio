# -*- coding: utf-8 -*-

from django import template
from projects.models import Description

register = template.Library()

@register.filter(is_safe=True)
def get_safe_html(description_object):
    return description_object.get_safe_html()

