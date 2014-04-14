import os, sys
import subprocess

from django.conf import settings
from projects.models import Code, SourceCode, Repository, SourceToTechnoLines, Technology

def extract_sourcecode(sourcecode):
    """
    Extract SourceCode's archive to the current working directory
    """

    # Untar the tar.gz file
    media_path = settings.MEDIA_ROOT
    if sourcecode.archive.name.endswith(".tar.gz"):
        untar_process = subprocess.Popen(['tar', 'zxf', os.path.join(media_path, sourcecode.archive.name)])
    elif sourcecode.archive.name.endswith(".zip"):
        untar_process = subprocess.Popen(['unzip', '-qq', '-u', os.path.join(media_path, sourcecode.archive.name), '-d', os.getcwd()])
    untar_process.wait()

def extract_repository(repository):
    """
    Clone repository to the current working directory
    """
    
    if repository.software == "git":
        clone_process = subprocess.Popen(['git', 'clone', '--quiet', repository.url])
    elif repository.software == "hg":
        clone_process = subprocess.Popen(['hg', 'clone', '--noninteractive', '--quiet', repository.url])
    elif repository.software == "zip":
        pass # TODO requests.head If-Modified-Since: Sat, 29 Oct 1994 19:43:31 GMT => 304..

    clone_process.wait()

def count_lines(code, rm_required=True):
    """
    Count the number of lines for each (root/main) programming language
    in a given source code
    """
   
    # Get real object (code_cast) and Code (code)

    if code.lines_ready:
        return
    
    if isinstance(code, SourceCode):
        code_cast = code
        code = Code.objects.get(id=code_cast.pk)
    elif isinstance(code, Repository):
        code_cast = code
        code = Code.objects.get(id=code_cast.pk)
    else:
        code_cast = code.cast()
        if not isinstance(code_cast, SourceCode) and not isinstance(code_cast, Repository):
            return

    # Project Directory

    media_path = settings.MEDIA_ROOT
    # "unzipped" project directory
    dir_path = os.path.join(media_path, "sourcecode", "sc_%d" % code.pk)

    # Create project directory if it does not exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # Change current working directory for projectdirectory
    os.chdir(dir_path)
    
    # Extraction
    
    if isinstance(code_cast, SourceCode):
        extract_sourcecode(code_cast)
    elif isinstance(code_cast, Repository):
        extract_repository(code_cast)
    
    # Count lines
    
    os.chdir(dir_path)

    # Delete everything that was already computed for that SourceCode
    SourceToTechnoLines.objects.filter(code=code).delete()
    
    # Technology by Technology
    technologies_to_analyse = Technology.objects.filter(parent_technology__isnull=True)
    for techno in technologies_to_analyse:
        if not techno.file_extensions:
            continue
        
        # Getting file-list:
        # find /home/django-portfolio/ -type f \( -regextype posix-extended -regex ".*\.(js|css)" -not -path "*/exclude/*" \)
     
        cmd_find = ["find", ".", "-type", "f", "(", "-regextype", "posix-extended", "-regex", ".*\.(%s)" % techno.file_extensions]
        exclude_paths_list = code.exclude_paths.split('\r\n')
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
                SourceToTechnoLines(code=code, technology=techno, num_lines=num_lines).save()
        except ValueError:
            pass
        except TypeError:
            pass

    # Supprime les fichiers extraits
    
    if rm_required:
        del_process = subprocess.Popen(["rm", "-rf", dir_path])
        del_process.wait()
    
    code.lines_ready = True
    code.save()

