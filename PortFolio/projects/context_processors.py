# -*- coding: utf-8 -*-
from django.conf import settings

def my_context_processor(request):
    return {
            "HEADER_ADMIN": settings.HEADER_ADMIN,
            "HEADER_QUICKLINKS": settings.HEADER_QUICKLINKS,
            "FOOTER_TEXT": settings.FOOTER_TEXT,
            "FOOTER_QUICKLINKS": settings.FOOTER_QUICKLINKS,
           }

