# -*- coding: utf-8 -*-

# Polymorphisme with DJANGO:
# + http://stackoverflow.com/questions/1397537/polymorphism-in-django
# + http://stackoverflow.com/questions/929029/how-do-i-access-the-child-classes-of-an-object-in-django-without-knowing-the-nam/929982#929982

import os
import re
import sys
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from projects.CustomFileField import CustomFileField

def log(text):
    print >>sys.stderr, text

class Category(models.Model): #eg.: Security/Game/Network..
    name = models.CharField(max_length=50, help_text=_("Category name"))
    name_url = models.CharField(max_length=20, help_text=_("Category name (URL)"))

    def __unicode__(self):
        return self.name

class Technology(models.Model): #eg.: C/SDL/Java..
    name = models.CharField(max_length=50, help_text=_("Technology name"))
    name_url = models.CharField(max_length=20, help_text=_("Technology name (URL)"))
    
    parent_technology = models.ForeignKey('self', blank=True, null=True, help_text=_("eg. Python is a parent technology for Django"))
    file_extensions = models.CharField(max_length=50, blank=True, null=True, help_text=_("Possible file extensions (eg. 'txt') separated by '|' (eg. 'js|css')"))

    def __unicode__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=50, help_text=_("Project name"))
    name_url = models.CharField(max_length=20, help_text=_("Project name (URL)"))
    short_description = models.CharField(max_length=155, help_text=_("Short description (max. 155)"))
    year = models.IntegerField(help_text=_("Release date"))
    
    private = models.BooleanField(default=True, help_text=_("Private => visible only if logged in"))
    
    category = models.ForeignKey(Category, help_text=_("Category"))
    technologies = models.ManyToManyField(Technology, help_text=_("Technologies"))
    
    def update_technologies(self):
        """
        Add missing Technology to the M2M relation
        eg. Django => Python
        
        Initially I tried to do it by overloading .save() method of Project
        I also tried to put signals listeners on .pre_save and .post_save()
        None of these technics worked
        """

        update_required = False

        technos = list(self.technologies.all())
        for techno in technos:
            if techno.parent_technology and techno.parent_technology not in technos:
                technos.append(techno.parent_technology)
                self.technologies.add(techno.parent_technology)
                update_required = True

        if update_required:
            self.save()

    def __unicode__(self):
        return self.name

@receiver(pre_delete, sender=Project, dispatch_uid='project_delete_signal')
def pre_delete_project(sender, instance, using, **kwargs):
    """
    Normally these commands should be done by Django itself,
    it is just to make sure that everything is deleted properly
    """

    instance.download_set.all().delete()
    instance.description_set.all().delete()

class Download(models.Model):
    def upload_path(self, filename):
        if self.project:
            return os.path.join('downloads', str(self.project.id), filename)
        else:
            return os.path.join('downloads', filename)
    
    project = models.ForeignKey(Project, blank=True, null=True, help_text=_("Linked to the project"))
    down = models.FileField(upload_to=upload_path, help_text=_("Downloadable file"))

@receiver(pre_delete, sender=Download, dispatch_uid='download_delete_signal')
def pre_delete_download(sender, instance, using, **kwargs):
    if os.path.isfile(instance.down.path):
        os.remove(instance.down.path)

class SourceCode(models.Model):
    """
    Source Code objects store the source code of a given project (tar.gz/zip file extension)
    Its content should be accessible only by authentificated people
    """

    def upload_path(self, filename):
        if filename.endswith(".zip"):    
            return os.path.join('sourcecode', str(self.project.id), '%s_%d.zip' % (filename[:-4], self.project.sourcecode_set.count()))
        
        return os.path.join('sourcecode', str(self.project.id), '%s_%d.tar.gz' % (filename[:-7], self.project.sourcecode_set.count()))
    
    project = models.ForeignKey(Project, help_text=_("Linked to the project"))
    archive = CustomFileField(upload_to=upload_path, file_extensions=["tar.gz", "zip"], help_text=_("Source Code (*.tar.gz/*.zip) of your project"))
    upload_time = models.DateTimeField(auto_now_add=True)
    exclude_paths = models.TextField(blank=True, null=True, help_text=_("Paths to exclude, one per line (eg.: */static/bootstrap/*)"))
    lines_ready = models.BooleanField(default=False)

    def __unicode__(self):
        return self.archive.name

    class Meta:
        ordering = ["-upload_time",]

class SourceToTechnoLines(models.Model):
    """
    Number of lines for a given (SourceCode, Technology) pair
    """
    
    sourcecode = models.ForeignKey(SourceCode, help_text=_("Source code described"))
    technology = models.ForeignKey(Technology, help_text=_("Technology concerned"))
    num_lines = models.IntegerField(help_text=_("Number of lines of a given technology in a source code"))
    
    def __unicode__(self):
        return "%d lines of %s" % (self.num_lines, self.technology.name)
    
    class Meta:
        # A given pair cannot have several values for num_lines
        unique_together = ("sourcecode", "technology")

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
    project = models.ForeignKey(Project, help_text=_("Project"))
    position = models.IntegerField(default=0, help_text=_("Description's position (the smallest at the top, default value implies last one)"))
    data_anchor = models.CharField(max_length=50, blank=True, null=True, help_text=_("Data-anchor value (used to generate the wavy-menu) - optional"))
    
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
    description = models.TextField(help_text=_("Description - Raw Text"))
    description_html = models.TextField(help_text=_("HTML code automatically generated"))

    def rawtext_to_html(self):
        """
        This templatetag converts every url in text to an hyperlink.
        The text is escaped for HTML before adding hyperlinks.

        URL to link/image
        -----------------
        
        INPUT: need to start with a space or new line..
            Please visit: http://portfolio.dubien.me/
        OUTPUT:
            <p>Please visit: <a href="http://portfolio.dubien.me/" target="blank_">http://portfolio.dubien.me/</a></p>
        
        INPUT:
            ![my favicon](http://portfolio.dubien.me/favicon.ico)
        OUTPUT:
            <p><img src="http://portfolio.dubien.me/favicon.ico" alt="my favicon" class="image_from_rawtext" /></p>

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
        
        INPUT:
            This is a list:
            + 1
            + + 1.1
            + + 1.2
            + 2
        Output:
            <p>This is a list:</p><ul><li>1<ul><li>1.1</li><li>1.2</li></ul></li><li>2</li></ul>

        Italic/Bold
        -----------

        INPUT:
            This text is *italic* and this one **bold**.
        OUTPUT:
            <p>This text is <i>italic</i> and this one <b>bold</b>.</p>
        """
        
        parent = super(RawTextDescription, self)

        escaped_text = escape(self.description)

        # URL to link/image

        escaped_text = re.sub(r'(?P<begin>^|\n|\s)(?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', '\g<begin><a href="\g<url>" target="blank_">\g<url></a>', escaped_text)
        escaped_text = re.sub(r'!\[(?P<alt>[^\]]*)\]\((?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\)', '<img src="\g<url>" alt="\g<alt>" class="image_from_rawtext" />', escaped_text)
        escaped_text = re.sub(r'\[(?P<title>[^\]]+)\]\((?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\)', '<a href="\g<url>" target="blank_">\g<title></a>', escaped_text)
        
        # Bulletpoints to list
        
        before = escaped_text
        escaped_text = re.sub(r'\n\+\s(?P<li_element>[^\n]+)', '</p><ul><li>\g<li_element></li></ul><p>', escaped_text).replace('</ul><p></p><ul>', '')
        
        # Other levels for bulletpoints
        while before != escaped_text:
            before = escaped_text

            # pattern: <li>+ xxxxxxxxx</li>
            # < cannot be find in the original text (escaped)
            escaped_text = re.sub(r'<li>\+\s(?P<li_element>[^<]+)</li>', '<ul><li>\g<li_element></li></ul>', escaped_text).replace('</ul><ul>', '')
            
            # This part computes the corresponding valid syntax for nested lists
            # the current value of escaped_text should already be fine for most of the browsers

            # We will get something like:
            # <ul><li>1</li><ul><li>1.1</li></ul></ul>
            # instead of:
            # <ul><li>1<ul><li>1.1</li></ul></li></ul>
            escaped_text = re.sub(r'</li><ul>(?P<li_elements>.+)</ul>', '<ul>\g<li_elements></ul></li>', escaped_text)
            # or:
            # <ul><ul><li>1.1</li></ul></ul>
            # instead of:
            # <ul><li><ul><li>1.1</li></ul></li></ul>
            escaped_text = re.sub(r'<ul><ul>(?P<li_elements>.+)</ul>', '<ul><li><ul>\g<li_elements></ul></li>', escaped_text)

        del before

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

    def save(self, *args, **kwargs):
        """
        Redefinite .save() method of RawTextDescription
        Automatically generates description_html when saving an object
        """

        self.description_html = self.rawtext_to_html()
        super(Description, self).save(*args, **kwargs)
    
    def get_safe_html(self, parent=None):
        """
        Return the HTML description
        if not generated (possible with older versions) generate it and save it
        """
        
        if self.description and not self.description_html:
            self.save() # save will call rawtext_to_html

        return self.description_html

class HtmlCodeDescription(Description):
    description = models.TextField(help_text=_("Description - Html Code"))

    def get_safe_html(self, parent=None):
        return self.description

class ImageDescription(Description):
    def upload_path(self, filename):
        parent = super(ImageDescription, self)
        return os.path.join('description', str(parent.project.id), filename)

    image = models.ImageField(upload_to=upload_path, help_text=_("Image"))
    legend = models.CharField(max_length=150, help_text=_("Image legend"))
    
    def get_safe_html(self):
        return """<p class="image"><img src="/media/%s" alt="%s" /><br/><span class="legend">%s</span></p>""" % (escape(self.image), escape(self.legend), escape(self.legend))

@receiver(pre_delete, sender=ImageDescription, dispatch_uid='imagedescription_delete_signal')
def pre_delete_imagedescription(sender, instance, using, **kwargs):
    if os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

