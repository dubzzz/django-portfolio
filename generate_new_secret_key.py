#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import re

secret_key = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
print "SECRET_KEY \033[92mgenerated\033[0m"
with open('PortFolio/PortFolio/settings.py', 'a+') as settings_file:
    current_settings = settings_file.read()
    new_settings = re.sub(r"SECRET_KEY[ ]*=[ ]*'[^']*'", "SECRET_KEY='%s'" % secret_key, current_settings)
    if current_settings != new_settings:
        settings_file.truncate(0)
        settings_file.write(new_settings)
        print "SECRET_KEY \033[92madded to settings.py\033[0m"
    else:
        print "\033[91mFailed to find the field SECRET_KEY in settings.py\033[0m"

