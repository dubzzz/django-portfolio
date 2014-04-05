#!/usr/bin/python

# Setup Django Environment

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),'../'))

from PortFolio import settings
from django.core.management import setup_environ

setup_environ(settings)

# Import useful modules

import subprocess
from projects.models import SourceCode, SourceToTechnoLines, Technology

# Retrieve SourceCode details

try:
    sourcecode_id = int(sys.argv[1])
    sourcecode = SourceCode.objects.get(pk=int(sourcecode_id))
except IndexError, e:
    print "ERROR - IndexError"
    print e
    print "Syntax: ./script_count_lines.py <sourcecode_id>"
    sys.exit(1)
except ValueError, e:
    print "ERROR - ValueError"
    print e
    print "Syntax: ./script_count_lines.py <sourcecode_id>"
    sys.exit(2)
except TypeError, e:
    print "ERROR - TypeError"
    print e
    print "Syntax: ./script_count_lines.py <sourcecode_id>"
    sys.exit(3)
except SourceCode.DoesNotExist, e:
    print "ERROR - DoesNotExist"
    print e
    sys.exit(4)

# Untar the file

# Media directory
media_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../media/")
# "Untar" directory
dir_path = os.path.join(media_path, "sourcecode", "sc_%d" % sourcecode_id)

# Create "untar" if it does not exist
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
# Change current working directory for "untar" directory
os.chdir(dir_path)

# Untar the tar.gz file
untar_process = subprocess.Popen(['tar', 'zxf', os.path.join(media_path, sourcecode.archive.name)])
untar_process.wait()

# Count #lines for each Technology

# Delete everything that was already computed for that SourceCode
SourceToTechnoLines.objects.filter(sourcecode=sourcecode).delete()

# Technology by Technology
technologies_to_analyse = Technology.objects.filter(parent_technology__isnull=True)
for techno in technologies_to_analyse:
    if not techno.file_extensions:
        continue
    
    # Getting file-list:
    # find /home/django-portfolio/ -type f \( -regextype posix-extended -regex ".*\.(js|css)" -not -path "*/exclude/*" \)
 
    cmd_find = ["find", ".", "-type", "f", "(", "-regextype", "posix-extended", "-regex", ".*\.(%s)" % techno.file_extensions]
    exclude_paths_list = sourcecode.exclude_paths.split('\n')
    for exclude_path in exclude_paths_list:
        if len(exclude_path) > 0:
            cmd_find += ["-not", "-path", exclude_path]
    cmd_find += [")", "-exec", "cat", "{}", ";"]

    ps_code_lines = subprocess.Popen(cmd_find, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ps_relevant_code_lines = subprocess.Popen(["grep", "-v", "^$"], stdin=ps_code_lines.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ps_count_lines = subprocess.Popen(["wc", "-l"], stdin=ps_relevant_code_lines.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    ps_code_lines.stdout.close() # allows ps_relevant_code_lines to receive a SIGPIPE if ps_code_lines exists
    ps_relevant_code_lines.stdout.close()
    
    try:
        # run the process and retrive its output
        num_lines = int(ps_count_lines.communicate()[0])
        if num_lines > 0:
            SourceToTechnoLines(sourcecode=sourcecode, technology=techno, num_lines=num_lines).save()
    except ValueError:
        print "%s <-> %s: Unable to count the number of lines" % (sourcecode.project.name, techno.name)
    except TypeError:
        print "%s <-> %s: Unable to count the number of lines" % (sourcecode.project.name, techno.name)

