# -*- coding: utf-8 -*-
from django.contrib import admin
from projects.models import *

admin.site.register(Category)
admin.site.register(Technology)
admin.site.register(Download)
admin.site.register(SourceCode)

class RawTextDescriptionInline(admin.StackedInline):
    model = RawTextDescription
    extra = 0
class HtmlCodeDescriptionInline(admin.StackedInline):
    model = HtmlCodeDescription
    extra = 0
class ImageDescriptionInline(admin.StackedInline):
    model = ImageDescription
    extra = 0

class DownloadInline(admin.StackedInline):
    model = Download
    extra = 0

class ProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'name_url']}),
        ('Détails élementaires', {'fields': ['short_description', 'year']}),
        ('Appartenance', {'fields': ['category', 'technologies']}),
    ]
    inlines = [RawTextDescriptionInline, HtmlCodeDescriptionInline, ImageDescriptionInline, DownloadInline]

admin.site.register(Project, ProjectAdmin)

