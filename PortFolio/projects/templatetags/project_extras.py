# -*- coding: utf-8 -*-

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

import re

register = template.Library()

@register.filter(is_safe=True)
def escape_project(text):
    """
    This templatetag converts every url in text to an hyperlink.
    The text is escaped for HTML before adding hyperlinks.

    URL to link
    -----------
    
    INPUT: need to start with a space or new line..
        Please visit: http://portfolio.dubien.me/
    OUTPUT:
        <p>Please visit: <a href="http://portfolio.dubien.me/" target="blank_">http://portfolio.dubien.me/</a></p>
    
    INPUT:
        [Click here](http://portfolio.dubien.me/) to try it!
    OUTPUT:
        <p><a href="http://portfolio.dubien.me/" target="blank_">Click here</a> to try it!</p>


    Bulletpoints to list
    --------------------
    
    INPUT:
        This is a list:
        + element 1
        + element 2
    OUTPUT:
        <p>This is a list:</p><ul><li>element 1</li><li>element 2</li></ul>
    """
    
    escaped_text = escape(text)

    # URL to link

    escaped_text = re.sub(r'(?P<begin>^|\n|\s)(?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', '\g<begin><a href="\g<url>" target="blank_">\g<url></a>', escaped_text)
    escaped_text = re.sub(r'\[(?P<title>[^\]]+)\]\((?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\)', '<a href="\g<url>" target="blank_">\g<title></a>', escaped_text)
    
    # Bulletpoints to list
    
    escaped_text = re.sub(r'\n\+\s(?P<li_element>[^\n]+)', '</p><ul><li>\g<li_element></li></ul><p>', escaped_text).replace('</ul><p></p><ul>', '')
    
    if escaped_text.endswith("<p>"):
        escaped_text = escaped_text[:-3]
    else:
        escaped_text += "</p>"
    
    if escaped_text.startswith("</p>"):
        escaped_text = escaped_text[4:]
    else:
        escaped_text = "<p>%s" % escaped_text
    
    return mark_safe(escaped_text)

