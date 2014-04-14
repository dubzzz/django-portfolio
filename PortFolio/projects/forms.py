# -*- coding: utf-8 -*-
from django import forms
from projects.models import *

class RawTextDescriptionForm(forms.ModelForm):
    class Meta:
        model = RawTextDescription
        fields = ('data_anchor', 'description',)

class HtmlCodeDescriptionForm(forms.ModelForm):
    class Meta:
        model = HtmlCodeDescription
        fields = ('data_anchor', 'description',)

class ImageDescriptionForm(forms.ModelForm):
    class Meta:
        model = ImageDescription
        fields = ('data_anchor', 'image', 'legend',)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = []

class DownloadForm(forms.ModelForm):
    class Meta:
        model = Download
        fields = ('down',)

class SourceCodeForm(forms.ModelForm):
    class Meta:
        model = SourceCode
        fields = ('archive', 'exclude_paths',)

class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ('software', 'url', 'exclude_paths',)

