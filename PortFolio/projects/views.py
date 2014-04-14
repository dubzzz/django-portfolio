# -*- coding: utf-8 -*-

import os
import sys
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Q, Count

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings

from multiprocessing import Process

from projects.forms import *
from projects.models import *
from projects.script_count_lines import count_lines

def home(request):
    if settings.STATS == "num_lines":
        sql_num_lines_per_techno = """
SELECT
	t.id,
	t.name,
    t.name_url,
	s2t_lines.num_lines AS num
FROM
	(
		SELECT
			s2t.technology_id AS id,
			SUM(s2t.num_lines) AS num_lines
		FROM projects_sourcetotechnolines AS s2t
		INNER JOIN
			(
				SELECT
					id,
					project_id
				FROM
					(
						SELECT id, project_id
						FROM projects_code
						ORDER BY projects_code.upload_time DESC
					) AS sc
				GROUP BY sc.project_id
			) AS last_codes
		ON
			s2t.code_id = last_codes.id
		GROUP BY s2t.technology_id
		ORDER BY num_lines
	) AS s2t_lines
LEFT JOIN projects_technology AS t
ON
	s2t_lines.id = t.id
ORDER BY num_lines DESC
LIMIT 3;
"""
        stats = Technology.objects.raw(sql_num_lines_per_techno)
    elif settings.STATS == "num_projects":
        stats = Technology.objects.filter(parent_technology__isnull=True).annotate(num=Count('project')).order_by('-num')[:3]
    
    if request.user.is_authenticated():
        return render_to_response('home.html', {"stats": stats, "projects": Project.objects.all().order_by("-year"), "empty_project_form": ProjectForm()}, context_instance=RequestContext(request))
    else:    
        return render_to_response('home.html', {"stats": stats, "projects": Project.objects.filter(private=False).order_by("-year")}, context_instance=RequestContext(request))

def show_project(request, project_url):
    if request.user.is_authenticated():
        project = get_object_or_404(Project, name_url=project_url)
        
        project_form = ProjectForm(instance=project)
        empty_download_form = DownloadForm()
        empty_sourcecode_form = SourceCodeForm()
        empty_repository_form = RepositoryForm()
        empty_forms = {
                "rawtext": {"name": "Raw Text", "form": RawTextDescriptionForm()},
                "htmlcode": {"name": "HTML Code", "form": HtmlCodeDescriptionForm()},
                "image": {"name": "Image", "form": ImageDescriptionForm()},
        }
        return render_to_response('project.html', {"project": project, "project_form": project_form, "empty_download_form": empty_download_form, "empty_sourcecode_form": empty_sourcecode_form, "empty_repository_form": empty_repository_form, "empty_forms": empty_forms}, context_instance=RequestContext(request))
    else:
        project = get_object_or_404(Project, name_url=project_url, private=False)
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
def add_project(request):
    """
    Add a new project
    """
    
    project = None
    # Check that the request has been transmitted in POST
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        
        # Check form validity
        if form.is_valid():
            project = form.save()
            project.update_technologies()
    
    if project:
        return HttpResponseRedirect(reverse('projects.views.show_project', args=[project.name_url]))
    else:    
        return HttpResponseRedirect(reverse('projects.views.home'))

@login_required
def update_project(request, project_id):
    """
    Update project's fields
    """

    project = get_object_or_404(Project, pk=project_id)
    
    # Check that the request has been transmitted in POST
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        
        # Check form validity
        if form.is_valid():
            p = form.save()
            p.update_technologies()

    return HttpResponseRedirect(reverse('projects.views.show_project', args=[project.name_url]))

@login_required
def delete_project(request, project_id):
    """
    Delete project
    """
    
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    return HttpResponseRedirect(reverse('projects.views.home'))

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
    
    real_description.delete() # pre_delete is automatically called to delete files (if required)

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

@login_required
def add_download_to(request, project_id):
    """
    Add download to a project
    """
    
    project = get_object_or_404(Project, pk=project_id)
    
    # Check that the request has been transmitted in POST
    if request.method == 'POST':
        form = DownloadForm(request.POST, request.FILES)
        # Check form validity
        if form.is_valid():
            down = form.save(commit=False)
            down.project = project
            down.save()
    
    return HttpResponseRedirect(reverse('projects.views.show_project', args=[project.name_url]))

@login_required
def delete_download(request, download_id):
    """
    Delete the download
    """
    
    down = get_object_or_404(Download, pk=download_id)
    project = down.project
    
    down.delete() # pre_delete is automatically called to delete files (if required)

    return HttpResponseRedirect(reverse('projects.views.show_project', args=[project.name_url]))

@login_required
def add_sourcecode_to(request, project_id):
    """
    Add sourcecode to a project
    """
    
    project = get_object_or_404(Project, pk=project_id)
    
    # Check that the request has been transmitted in POST
    if request.method == 'POST':
        form = SourceCodeForm(request.POST, request.FILES)
        # Check form validity
        if form.is_valid():
            sc = form.save(commit=False)
            sc.project = project
            sc.save()
            
            # Execute counting-lines operation
            p = Process(target=count_lines, args=(sc, True,))
            p.start()

    return HttpResponseRedirect(reverse('projects.views.show_project', args=[project.name_url]))

@login_required
def add_repository_to(request, project_id):
    """
    Add repository to a project
    """
    
    project = get_object_or_404(Project, pk=project_id)
    
    # Check that the request has been transmitted in POST
    if request.method == 'POST':
        form = RepositoryForm(request.POST, request.FILES)
        # Check form validity
        if form.is_valid():
            sc = form.save(commit=False)
            sc.project = project
            sc.save()
            
    return HttpResponseRedirect(reverse('projects.views.show_project', args=[project.name_url]))

@login_required
def get_code_lines(request, code_id):
    """
    Retrieve code's details
    """
    
    return render_to_response('sourcecode_lines.xml', {"lines": SourceToTechnoLines.objects.filter(code__id=code_id, code__lines_ready=True)}, context_instance=RequestContext(request), mimetype="application/xml")

