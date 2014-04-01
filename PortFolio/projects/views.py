# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.contrib import auth
from django.contrib.auth.decorators import login_required

from projects.models import *

def home(request):
    return render_to_response('home.html', {"projects": Project.objects.all().order_by("-year")}, context_instance=RequestContext(request))

def show_project(request, project_url):
    project = get_object_or_404(Project, name_url=project_url)
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

