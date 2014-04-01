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

