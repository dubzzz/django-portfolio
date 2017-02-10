#!/usr/bin/python

from os import path
import sys

from tornado.ioloop import IOLoop
from tornado.web import StaticFileHandler, Application, url
from config import COOKIE_SECRET

__CURRENT_PATH = path.dirname(__file__)
__CURRENT_ABSPATH = path.dirname(path.realpath(__file__))
__STATIC_ABSPATH = path.join(__CURRENT_ABSPATH, "static")
__TEMPLATES_ABSPATH = path.join(__CURRENT_ABSPATH, "templates")

sys.path.append(path.join(__CURRENT_PATH, "views"))
from auth import LoginHandler, LogoutHandler
from projects import HomeHandler, ProjectHandler, PerYearHandler, ErrorHandler

sys.path.append(path.join(__CURRENT_PATH, "views", "modules"))
import uimodules

settings = {
    "cookie_secret": COOKIE_SECRET,
    "login_url": "/login",
    "template_path": __TEMPLATES_ABSPATH,
    "ui_modules": uimodules,
    "xsrf_cookies": True,
}

application = Application([
    url(r"/", HomeHandler, name="home"),
    #url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}),
    #url('^edit/project/(?P<project_id>\d+)/add/download/$', 'add_download_to'),
    #url('^edit/project/(?P<project_id>\d+)/add/sourcecode/$', 'add_sourcecode_to'),
    #url('^edit/project/(?P<project_id>\d+)/add/repository/$', 'add_repository_to'),
    #url('^edit/project/(?P<project_id>\d+)/add/(?P<description_type>\w+)/$', 'add_description_to'),
    #url('^edit/description/(?P<description_id>\d+)/$', 'update_description'),
    #url('^edit/project/(?P<project_id>\d+)/$', 'update_project'),
    #url('^add/project/$', 'add_project'),
    #url('^delete/description/(?P<description_id>\d+)/$', 'delete_description'),
    #url('^delete/download/(?P<download_id>\d+)/$', 'delete_download'),
    #url('^delete/project/(?P<project_id>\d+)/$', 'delete_project'),
    #url('^moveup/description/(?P<description_id>\d+)/$', 'move_up_description'),
    #url('^movedown/description/(?P<description_id>\d+)/$', 'move_down_description'),
    #url('^project/(?P<project_url>[^/]+)/$', 'show_project_depreciated'),
    url(r"/(?P<year>\d{4})/(?P<project_url>[^/]+).html", ProjectHandler, name="show_project"),
    url(r"/(?P<year>\d{4})/", PerYearHandler, name="show_projects_year"),
    url(r"/error/(?P<error_code>\d{3}).html", ErrorHandler, name="error_code"),
    #url('^get/code/lines/(?P<code_id>\d+)/$', 'get_code_lines'),
    url(r"/login", LoginHandler, name="login"),
    url(r"/logout", LogoutHandler, name="logout"),
    url(r'/static/(.*)', StaticFileHandler, {'path': __STATIC_ABSPATH}),
], **settings)

if __name__ == "__main__":
    if len(sys.argv) != 1 and len(sys.argv) != 2:
        print('''Syntax: ./start.py <port=8080>''')
        exit(1)
    
    try:
        if (len(sys.argv) == 2):
            port = int(sys.argv[1])
        else:
            port = 8080
    except ValueError, e:
        print('''ERROR: {}'''.format(e))
        print('''Syntax: ./start.py <port=8080>''')
        exit(2)
    except TypeError, e:
        print('''ERROR: {}'''.format(e))
        print('''Syntax: ./start.py <port=8080>''')
        exit(3)
    
    # Start the server
    application.listen(port)
    IOLoop.instance().start()

