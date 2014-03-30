# -*- coding: utf-8 -*-

import os
from django.db import models

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

class Download(models.Model):
    def upload_path(self, filename):
        if self.project:
            return os.path.join('downloads', str(self.project.id), filename)
        else:
            return os.path.join('downloads', filename)
    
    project = models.ForeignKey(Project, blank=True, null=True, help_text="Projet concerné")
    down = models.FileField(upload_to=upload_path, help_text="Fichier pouvant être téléchargé par l'utilisateur")

