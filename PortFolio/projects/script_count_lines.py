import os, sys
import subprocess

from django.conf import settings
from projects.models import Code, SourceCode, SourceToTechnoLines, Technology

def count_lines(sourcecode, rm_required=True):
    """
    Count the number of lines for each (root/main) programming language
    in a given source code
    """
    
    if sourcecode.lines_ready:
        sourcecode.lines_ready = False
        sourcecode.save()

    # Untar/Unzip the file

    media_path = settings.MEDIA_ROOT
    # "Untar" directory
    dir_path = os.path.join(media_path, "sourcecode", "sc_%d" % sourcecode.pk)

    # Create "untar" if it does not exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # Change current working directory for "untar" directory
    os.chdir(dir_path)

    # Untar the tar.gz file
    if sourcecode.archive.name.endswith(".tar.gz"):
        untar_process = subprocess.Popen(['tar', 'zxf', os.path.join(media_path, sourcecode.archive.name)])
    elif sourcecode.archive.name.endswith(".zip"):
        untar_process = subprocess.Popen(['unzip', '-u', os.path.join(media_path, sourcecode.archive.name), '-d', dir_path])
    untar_process.wait()

    # Count #lines for each Technology
    
    # Delete everything that was already computed for that SourceCode
    SourceToTechnoLines.objects.filter(code=sourcecode.pk).delete()
    
    # Technology by Technology
    technologies_to_analyse = Technology.objects.filter(parent_technology__isnull=True)
    for techno in technologies_to_analyse:
        if not techno.file_extensions:
            continue
        
        # Getting file-list:
        # find /home/django-portfolio/ -type f \( -regextype posix-extended -regex ".*\.(js|css)" -not -path "*/exclude/*" \)
     
        cmd_find = ["find", ".", "-type", "f", "(", "-regextype", "posix-extended", "-regex", ".*\.(%s)" % techno.file_extensions]
        exclude_paths_list = sourcecode.exclude_paths.split('\r\n')
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
                SourceToTechnoLines(code=Code.objects.get(id=sourcecode.pk), technology=techno, num_lines=num_lines).save()
        except ValueError:
            pass
        except TypeError:
            pass
    
    # Supprime les fichiers extraits
    
    if rm_required:
        del_process = subprocess.Popen(["rm", "-rf", dir_path])
        del_process.wait()
    
    sourcecode.lines_ready = True
    sourcecode.save()

