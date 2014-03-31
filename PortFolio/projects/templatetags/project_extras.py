# -*- coding: utf-8 -*-

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

import re

register = template.Library()

@register.filter(is_safe=True)
def url_to_link(text):
    """
    This templatetag converts every url in text to an hyperlink.
    The text is escaped for HTML before adding hyperlinks.

    INPUT:
        Please visit: http://portfolio.dubien.me/
    OUTPUT:
        Please visit: <a href="http://portfolio.dubien.me/" target="blank_">http://portfolio.dubien.me/</a>
    """
    
    escaped_text = escape(text)
    return mark_safe(re.sub(r'(?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', '<a href="\g<url>" target="blank_">\g<url></a>', escaped_text))

