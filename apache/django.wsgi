import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../PortFolio/"))
os.environ['DJANGO_SETTINGS_MODULE'] = 'PortFolio.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
