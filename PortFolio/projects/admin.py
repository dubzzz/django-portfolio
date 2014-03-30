# -*- coding: utf-8 -*-
from django.contrib import admin
from projects.models import *

admin.site.register(Category)
admin.site.register(Technology)
admin.site.register(Download)

class SubDescriptionInline(admin.StackedInline):
    model = SubDescription
    extra = 1

class DownloadInline(admin.StackedInline):
    model = Download
    extra = 0

class ProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'name_url']}),
        ('Détails élementaires', {'fields': ['short_description', 'year']}),
        ('Appartenance', {'fields': ['category', 'technologies']}),
    ]
    inlines = [SubDescriptionInline, DownloadInline]

admin.site.register(Project, ProjectAdmin)

