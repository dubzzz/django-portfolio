from django.conf.urls import patterns, include, url

urlpatterns = patterns('projects.views',
    url('^$', 'home'),
    url('^project/(?P<project_url>[^/]+)/$', 'show_project'),
)

