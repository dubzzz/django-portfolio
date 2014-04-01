# -*- coding: utf-8 -*-

from django import template
from django.template import Context
from django.template.loader import get_template

register = template.Library()

@register.filter
def as_bootstrap(form, prefixe="input"):
	"""
	Shaping a form
	
	{{ form|as_bootstrap:"prefixe" }}
	"""
	
	return get_template("form_bootstrap.html").render(Context({'form': form, 'prefixe':prefixe}))

