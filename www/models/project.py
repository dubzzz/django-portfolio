import re
import sqlite3
import sys
from datetime import datetime
from os import path
from tornado.escape import utf8, _unicode, xhtml_escape, url_escape

__CURRENT_PATH = path.dirname(__file__)

from project_summary import ProjectSummary

sys.path.append(path.join(__CURRENT_PATH, "..", "scripts"))
from generate_db import DEFAULT_DB

class Project(ProjectSummary):
    def __init__(self, year, name_url, name, short_description, private, modified, category):
        super(Project, self).__init__(year, name_url, name, short_description, private)
        self.category = category
        self.technologies = list()
        self.descriptions = list()
        self.downloads = list()
        self.modified = modified

class Description(object):
    def __init__(self, anchor):
        self.anchor = anchor
    
    def wrap(self, escaped_text):
        if self.anchor and len(self.anchor) > 0:
            escaped_text = re.sub(r'^<(?P<details>[^>]+)>', '<\g<details> data-anchor="%s">' % self.anchor, escaped_text)
        return utf8(escaped_text) #.encode('ascii')

class ImageContent(Description):
    def __init__(self, anchor, image, legend):
        super(ImageContent, self).__init__(anchor)
        self.image = image
        self.legend = legend
    
    def __str__(self):
        escaped_url = '/'.join([url_escape(elt) for elt in self.image.split('/')])
        return self.wrap("""<p class="image"><img src="/media/%s" alt="%s" /><br/><span class="legend">%s</span></p>""" % (escaped_url, xhtml_escape(self.legend), xhtml_escape(self.legend)))

class HtmlCode(Description):
    def __init__(self, anchor, description):
        super(HtmlCode, self).__init__(anchor)
        self.description = description
    
    def __str__(self):
        return self.wrap(self.description)

class RawText(Description):
    def __init__(self, anchor, description, htmlcode):
        super(RawText, self).__init__(anchor)
        self.description = description
        self.htmlcode = htmlcode
    
    def __str__(self):
        return self.wrap(self.htmlcode)

class Download(object):
    def __init__(self, url):
      self.url = url
    
    def __str__(self):
      return utf8(self.url)

def project_from_query(data):
    year = data[0]
    name_url = data[1]
    name = data[2]
    short_description = data[3]
    private = data[4]
    modified = data[5]
    category = data[6]
    return Project(year, name_url, name, short_description, private, modified, category)

def description_from_query(data):
    model = data[0]
    position = int(data[1])
    anchor = data[2]
    if model == "imagedescription":
        return (position, ImageContent(anchor, data[6], data[7]))
    elif model == "htmlcodedescription":
        return (position, HtmlCode(anchor, data[5]))
    elif model == "rawtextdescription":
        return (position, RawText(anchor, data[3], data[4]))

def download_from_query(data):
    return (int(data[0]), data[1])

def load_project(year, project_url, private_only):
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        
        # Load basic project details
        
        query = '''SELECT proj.year, proj.name_url, proj.name, proj.short_description, proj.private, proj.modified, cat.name, proj.id
                   FROM projects_project AS proj
                   INNER JOIN projects_category AS cat
                       ON proj.category_id = cat.id
                   WHERE proj.year=? AND proj.name_url=?'''
        parameters = (year, project_url,)
        if private_only:
            query += ''' AND proj.private=?'''
            parameters += (False,)
        c.execute(query, parameters)
        
        data = c.fetchone()
        if data is None:
            return None
        
        pid = int(data[7])
        p = project_from_query(data)
        
        # Append technologies
        
        c.execute('''SELECT tech.name
                   FROM projects_technology AS tech
                   INNER JOIN projects_project_technologies AS j
                       ON j.technology_id = tech.id
                   WHERE j.project_id = ?''', (pid,))
        p.technologies = [data[0] for data in c.fetchall()]
        
        # Append descriptions
        
        c.execute('''SELECT dj.model, desc.position, desc.data_anchor, raw.description, raw.description_html, html.description, img.image, img.legend
                    FROM projects_description AS desc
                    INNER JOIN django_content_type AS dj
                        ON dj.id = desc.real_type_id
                    LEFT JOIN projects_rawtextdescription AS raw
                        ON raw.description_ptr_id = desc.id
                    LEFT JOIN projects_htmlcodedescription AS html
                        ON html.description_ptr_id = desc.id
                    LEFT JOIN projects_imagedescription AS img
                        ON img.description_ptr_id = desc.id
                    WHERE desc.project_id = ?
                    ORDER BY desc.position''', (pid,))
        p.descriptions = [description_from_query(data) for data in c.fetchall()]
        
        # Append downloads
                
        c.execute('''SELECT down.id, down.down
                   FROM projects_download AS down
                   WHERE down.project_id = ?''', (pid,))
        p.downloads = [download_from_query(data) for data in c.fetchall()]
        
        return p
    return None

