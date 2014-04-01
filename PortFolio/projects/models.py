# -*- coding: utf-8 -*-

# Polymorphisme with DJANGO:
# + http://stackoverflow.com/questions/1397537/polymorphism-in-django
# + http://stackoverflow.com/questions/929029/how-do-i-access-the-child-classes-of-an-object-in-django-without-knowing-the-nam/929982#929982

import os
import re
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape
from django.utils.safestring import mark_safe

class Category(models.Model): #eg.: Security/Game/Network..
    name = models.CharField(max_length=50, help_text="Nom de la catégorie")
    name_url = models.CharField(max_length=20, help_text="Nom de la catégorie (URL)")

    def __unicode__(self):
        return self.name

class Technology(models.Model): #eg.: C/SDL/Java..
    name = models.CharField(max_length=50, help_text="Nom de la technologie")
    name_url = models.CharField(max_length=20, help_text="Nom de la technologie (URL)")
    
    def __unicode__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=50, help_text="Nom du projet")
    name_url = models.CharField(max_length=20, help_text="Nom du projet (URL)")
    short_description = models.CharField(max_length=155, help_text="Court descriptif")
    year = models.IntegerField(help_text="Année de lancement du projet")
    
    category = models.ForeignKey(Category, help_text="Catégorie à laquelle appartient ce projet")
    technologies = models.ManyToManyField(Technology, help_text="Technologies liées à ce projet")
    
    def __unicode__(self):
        return self.name

class SubDescription(models.Model):
    def upload_path(self, filename):
        return os.path.join('description', str(self.project.id), filename)

    project = models.ForeignKey(Project, help_text="Projet concerné")
    
    html_description = models.BooleanField(default=False, help_text="Code HTML ?")
    description = models.TextField(blank=True, null=True, help_text="Description")
    
    image = models.ImageField(upload_to=upload_path, blank=True, null=True, help_text="Image")
    legend = models.CharField(max_length=150, blank=True, null=True, help_text="Légende de l'image")

    data_anchor = models.CharField(max_length=50, blank=True, null=True, help_text="Data-anchor pour le paragraphe ou l'image (pour non code-HTML)")

class Download(models.Model):
    def upload_path(self, filename):
        if self.project:
            return os.path.join('downloads', str(self.project.id), filename)
        else:
            return os.path.join('downloads', filename)
    
    project = models.ForeignKey(Project, blank=True, null=True, help_text="Projet concerné")
    down = models.FileField(upload_to=upload_path, help_text="Fichier pouvant être téléchargé par l'utilisateur")

class InheritanceCastModel(models.Model):
    """
    An abstract base class that provides a ``real_type`` FK to ContentType.
    For use in trees of inherited models, to be able to downcast
    parent instances to their child types.
    """

    real_type = models.ForeignKey(ContentType, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()
        super(InheritanceCastModel, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    class Meta:
        abstract = True

class Description(InheritanceCastModel):
    project = models.ForeignKey(Project, help_text="Projet concerné")
    position = models.IntegerField(default=0, help_text="Position de la description (plus faible => en haut), prend la valeur suivante si non définie ou égale à 0")
    data_anchor = models.CharField(max_length=50, blank=True, null=True, help_text="Data-anchor pour le paragraphe ou l'image (pour non code-HTML)")
    
    def save(self, *args, **kwargs):
        """
        Auto-defined position value, if not defined (or =0)
        """

        if not self.position:
            try:
                self.position = Description.objects.filter(project=self.project).order_by("-position")[0].position +1
            except:
                self.position = 1

        super(Description, self).save(*args, **kwargs)

    def get_safe_html(self):
        """
        Return a mark_safe string
        displaying the description
        """

        subclass = self.cast()
        escaped_text = subclass.get_safe_html()
        
        # Add data-anchor to paragraphs
        if self.data_anchor and len(self.data_anchor) > 0:
            escaped_text = re.sub(r'^<(?P<details>[^>]+)>', '<\g<details> data-anchor="%s">' % self.data_anchor, escaped_text)
        
        return mark_safe(escaped_text)

    class Meta:
        # Option abstract is not in use. Otherwise we would have one relation table for each child of that class
        # that is to say: projects_rawtextdescription, projects_htmlcodedescription, projects_imagedescription
        # instead of: projects_description
        # abstract = True
        ordering = ["position"]

class RawTextDescription(Description):
    description = models.TextField(help_text="Description")

    def get_safe_html(self, parent=None):
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
        
        Italic/Bold
        -----------

        INPUT:
            This text is *italic* and this one **bold**.
        OUTPUT:
            <p>This text is <i>italic</i> and this one <b>bold</b>.</p>
        """
        
        if not parent:
            parent = super(RawTextDescription, self)

        escaped_text = escape(self.description)

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
        
        # Italic/Bold
        
        escaped_text = re.sub(r'\*\*(?P<text>[^(\*\<\n)]+)\*\*', '<b>\g<text></b>', escaped_text)
        escaped_text = re.sub(r'\*(?P<text>[^(\*\<\n)]+)\*', '<i>\g<text></i>', escaped_text)
        
        return escaped_text

class HtmlCodeDescription(Description):
    description = models.TextField(help_text="Description")

    def get_safe_html(self, parent=None):
        return self.description

class ImageDescription(Description):
    def upload_path(self, filename):
        parent = super(ImageDescription, self)
        return os.path.join('description', str(parent.project.id), filename)

    image = models.ImageField(upload_to=upload_path, help_text="Image")
    legend = models.CharField(max_length=150, help_text="Légende de l'image")
    
    def get_safe_html(self):
        return """<p class="image"><img src="/media/%s" alt="%s" /><br/><span class="legend">%s</span></p>""" % (escape(self.image), escape(self.legend), escape(self.legend))

