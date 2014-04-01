# -*- coding: utf-8 -*-

from django import template
from projects.forms import *
from projects.models import Description, RawTextDescription, HtmlCodeDescription, ImageDescription

register = template.Library()

@register.filter(is_safe=True)
def get_safe_html(description_object):
    return description_object.get_safe_html()

@register.filter
def get_form(description_object):
    real_description_object = description_object.cast()

    if isinstance(real_description_object, RawTextDescription):
        return RawTextDescriptionForm(instance=real_description_object)
    elif isinstance(real_description_object, HtmlCodeDescription):
        return HtmlCodeDescriptionForm(instance=real_description_object)
    elif isinstance(real_description_object, ImageDescription):
        return ImageDescriptionForm(instance=real_description_object)

    return None

