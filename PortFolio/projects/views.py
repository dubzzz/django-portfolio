# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.contrib import auth
from django.contrib.auth.decorators import login_required

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
    
    # Check that the request hab been transmitted in POST
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

