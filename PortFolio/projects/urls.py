from django.conf.urls import patterns, include, url

urlpatterns = patterns('projects.views',
    url('^$', 'home'),
    url('^edit/project/(?P<project_id>\d+)/add/(?P<description_type>\w+)/$', 'add_description_to'),
    url('^project/(?P<project_url>[^/]+)/$', 'show_project'),
)

