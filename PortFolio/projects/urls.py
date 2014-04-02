from django.conf.urls import patterns, include, url

urlpatterns = patterns('projects.views',
    url('^$', 'home'),
    url('^edit/project/(?P<project_id>\d+)/add/(?P<description_type>\w+)/$', 'add_description_to'),
    url('^edit/description/(?P<description_id>\d+)/$', 'update_description'),
    url('^delete/description/(?P<description_id>\d+)/$', 'delete_description'),
    url('^moveup/description/(?P<description_id>\d+)/$', 'move_up_description'),
    url('^movedown/description/(?P<description_id>\d+)/$', 'move_down_description'),
    url('^project/(?P<project_url>[^/]+)/$', 'show_project'),
)

