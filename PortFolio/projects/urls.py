from django.conf.urls import patterns, include, url

urlpatterns = patterns('projects.views',
    url('^$', 'home'),
    url('^edit/project/(?P<project_id>\d+)/add/(?P<description_type>\w+)/$', 'add_description_to'),
    url('^edit/description/(?P<description_id>\d+)/$', 'update_description'),
    url('^project/(?P<project_url>[^/]+)/$', 'show_project'),
)

