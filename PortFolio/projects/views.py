# -*- coding: utf-8 -*-

import os
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Q

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError

from projects.forms import *
from projects.models import *

def home(request):
    return render_to_response('home.html', {"projects": Project.objects.all().order_by("-year")}, context_instance=RequestContext(request))

def show_project(request, project_url):
    project = get_object_or_404(Project, name_url=project_url)
    if request.user.is_authenticated():
        empty_forms = {"rawtext": RawTextDescriptionForm(), "htmlcode": HtmlCodeDescriptionForm(), "image": ImageDescriptionForm()}
        return render_to_response('project.html', {"project": project, "empty_forms": empty_forms}, context_instance=RequestContext(request))
    else:
        return render_to_response('project.html', {"project": project}, context_instance=RequestContext(request))

def logout(request):
    """
    Logout the user
    """

    auth.logout(request)
    if request.GET.has_key("next"):
        return HttpResponseRedirect(request.GET["next"])
    else:
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

@login_required
def add_description_to(request, project_id, description_type):
    """
    Add description to a project
    The description is added as last description
    """
    
    project = get_object_or_404(Project, pk=project_id)
    
    # Check that the request has been transmitted in POST
    if request.method == 'POST':
        form = None
        
        # Ajustments based on the kind of description
        if description_type == 'rawtext':
            form = RawTextDescriptionForm(request.POST)
        elif description_type == 'htmlcode':
            form = HtmlCodeDescriptionForm(request.POST)
        elif description_type == 'image':
            form = ImageDescriptionForm(request.POST, request.FILES)
         
        # Check form validity
        if form and form.is_valid():
            description_elt = form.save(commit=False)
            description_elt.project = project
            description_elt.save()
    
    return HttpResponseRedirect(reverse('projects.views.show_project', args=[project.name_url]))

@login_required
def update_description(request, description_id):
    """
    Modify/Change an existing description
    """

    description = get_object_or_404(Description, pk=description_id)
    
    # Check that the request has been transmitted in POST
    if request.method == 'POST':
        form = None
        real_description = description.cast()
        
        # Ajustments depending on the kind of description
        if isinstance(real_description, RawTextDescription):
            form = RawTextDescriptionForm(request.POST, instance=real_description)
        elif isinstance(real_description, HtmlCodeDescription):
            form = HtmlCodeDescriptionForm(request.POST, instance=real_description)
        elif isinstance(real_description, ImageDescription):
            form = ImageDescriptionForm(request.POST, instance=real_description)

        # Check form validity
        if form and form.is_valid():
            real_description = form.save(commit=False)
            try:
                if request.FILES['image'] and isinstance(real_description, ImageDescription):
                    if real_description.image:
                        os.remove(real_description.image.path)
                    real_description.image = request.FILES['image']
            except MultiValueDictKeyError, e:
                pass
            real_description.save()

    return HttpResponseRedirect(reverse('projects.views.show_project', args=[description.project.name_url]))

@login_required
def delete_description(request, description_id):
    """
    Delete the description
    """
    
    description = get_object_or_404(Description, pk=description_id)
    real_description = description.cast()

    project = description.project
    
    if isinstance(real_description, ImageDescription):
            os.remove(real_description.image.path)
    real_description.delete()

    return HttpResponseRedirect(reverse('projects.views.show_project', args=[project.name_url]))

def restore_descriptions_positions(project):
    current_pos = 1
    for desc in project.description_set.all():
        desc.position = current_pos
        desc.save()
        current_pos += 1

@login_required
def move_up_description(request, description_id):
    """
    Change the description's position field in order to have
    this description above the one just before
    """
    
    description = get_object_or_404(Description, pk=description_id)
    project = description.project
    
    # Get all the decriptions that are before
    try:
        prev_description = project.description_set.filter(Q(position__lt=description.position) | Q(pk__lt=description.pk, position=description.position)).order_by('-position')[0]
        
        # Recreate positions based on current position in the set before reordering anything
        if description.position == prev_description.position:
            restore_descriptions_positions(project)

            description = get_object_or_404(Description, pk=description_id)
            prev_description = project.description_set.filter(Q(position__lt=description.position) | Q(pk__lt=description.pk, position=description.position)).order_by('-position')[0]
        
        current_position = description.position
        description.position = prev_description.position
        prev_description.position = current_position
        
        description.save()
        prev_description.save()
        
    except IndexError, e:
        pass # The description is already the one at the top
    return HttpResponseRedirect(reverse('projects.views.show_project', args=[project.name_url]))

@login_required
def move_down_description(request, description_id):
    """
    Change the description's position field in order to have
    this description below the one just after
    """
    
    description = get_object_or_404(Description, pk=description_id)
    project = description.project
    
    # Get all the decriptions that are before
    try:
        prev_description = project.description_set.filter(Q(position__gt=description.position) | Q(pk__gt=description.pk, position=description.position)).order_by('position')[0]
        
        # Recreate positions based on current position in the set before reordering anything
        if description.position == prev_description.position:
            restore_descriptions_positions(project)

            description = get_object_or_404(Description, pk=description_id)
            prev_description = project.description_set.filter(Q(position__gt=description.position) | Q(pk__gt=description.pk, position=description.position)).order_by('position')[0]
        
        current_position = description.position
        description.position = prev_description.position
        prev_description.position = current_position
        
        description.save()
        prev_description.save()
        
    except IndexError, e:
        pass # The description is already the one at the top
    return HttpResponseRedirect(reverse('projects.views.show_project', args=[project.name_url]))

