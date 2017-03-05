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

def rawtext_to_html(description):
    """
    This templatetag converts every url in text to an hyperlink.
    The text is escaped for HTML before adding hyperlinks.

    URL to link/image
    -----------------
    
    INPUT: need to start with a space or new line..
        Please visit: http://portfolio.dubien.me/
    OUTPUT:
        <p>Please visit: <a href="http://portfolio.dubien.me/" target="blank_">http://portfolio.dubien.me/</a></p>
    
    INPUT:
        ![my favicon](http://portfolio.dubien.me/favicon.ico)
    OUTPUT:
        <p><img src="http://portfolio.dubien.me/favicon.ico" alt="my favicon" class="image_from_rawtext" /></p>

    INPUT:
        [Click here](http://portfolio.dubien.me/) to try it!
    OUTPUT:
        <p><a href="http://portfolio.dubien.me/" target="blank_">Click here</a> to try it!</p>


    Bulletpoints to list
    --------------------
    
    INPUT:
        This is a list:
        + element 1
        + element 2
    OUTPUT:
        <p>This is a list:</p><ul><li>element 1</li><li>element 2</li></ul>
    
    INPUT:
        This is a list:
        + 1
        + + 1.1
        + + 1.2
        + 2
    Output:
        <p>This is a list:</p><ul><li>1<ul><li>1.1</li><li>1.2</li></ul></li><li>2</li></ul>

    Italic/Bold
    -----------

    INPUT:
        This text is *italic* and this one **bold**.
    OUTPUT:
        <p>This text is <em>italic</em> and this one <strong>bold</strong>.</p>

    INPUT:
        This is a list:
        + 1
        + + 1.1
        + + 1.2
        + 2
    Output:
        <p>This is a list:</p><ul><li>1<ul><li>1.1</li><li>1.2</li></ul></li><li>2</li></ul>

    Italic/Bold
    -----------

    INPUT:
        This text is *italic* and this one **bold**.
    OUTPUT:
        <p>This text is <em>italic</em> and this one <strong>bold</strong>.</p>
    """
    
    escaped_text = xhtml_escape(description)

    # URL to link/image

    escaped_text = re.sub(r'(?P<begin>^|\n|\s)(?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', '\g<begin><a href="\g<url>" target="blank_">\g<url></a>', escaped_text)
    escaped_text = re.sub(r'!\[(?P<alt>[^\]]*)\]\((?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\)', '<img src="\g<url>" alt="\g<alt>" class="image_from_rawtext" />', escaped_text)
    escaped_text = re.sub(r'\[(?P<title>[^\]]+)\]\((?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\)', '<a href="\g<url>" target="blank_">\g<title></a>', escaped_text)
    
    # Bulletpoints to list
    
    before = escaped_text
    escaped_text = re.sub(r'\n\+\s(?P<li_element>[^\n]+)', '</p><ul><li>\g<li_element></li></ul><p>', escaped_text).replace('</ul><p></p><ul>', '')
    
    # Other levels for bulletpoints
    while before != escaped_text:
        before = escaped_text

        # pattern: <li>+ xxxxxxxxx</li>
        # < cannot be find in the original text (escaped)
        escaped_text = re.sub(r'<li>\+\s(?P<li_element>[^<]+)</li>', '<ul><li>\g<li_element></li></ul>', escaped_text).replace('</ul><ul>', '')
        
        # This part computes the corresponding valid syntax for nested lists
        # the current value of escaped_text should already be fine for most of the browsers

        # We will get something like:
        # <ul><li>1</li><ul><li>1.1</li></ul></ul>
        # instead of:
        # <ul><li>1<ul><li>1.1</li></ul></li></ul>
        escaped_text = re.sub(r'</li><ul>(?P<li_elements>.+)</ul>', '<ul>\g<li_elements></ul></li>', escaped_text)
        # or:
        # <ul><ul><li>1.1</li></ul></ul>
        # instead of:
        # <ul><li><ul><li>1.1</li></ul></li></ul>
        escaped_text = re.sub(r'<ul><ul>(?P<li_elements>.+)</ul>', '<ul><li><ul>\g<li_elements></ul></li>', escaped_text)

    del before

    if escaped_text.endswith("<p>"):
        escaped_text = escaped_text[:-3]
    else:
        escaped_text += "</p>"
    
    if escaped_text.startswith("</p>"):
        escaped_text = escaped_text[4:]
    else:
        escaped_text = "<p>%s" % escaped_text
    
    # Italic/Bold
    
    escaped_text = re.sub(r'\*\*(?P<text>[^(\*\<\n)]+)\*\*', '<strong>\g<text></strong>', escaped_text)
    escaped_text = re.sub(r'\*(?P<text>[^(\*\<\n)]+)\*', '<em>\g<text></em>', escaped_text)
    
    return escaped_text

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
        self.htmlcode = rawtext_to_html(self.description)
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

def delete_project(year, project_url):
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        c.execute('''SELECT id FROM projects_project WHERE year=? AND name_url=?''', (year, project_url,))
        data = c.fetchone()
        if data is None:
            return False
        pid = int(data[0])
        
        # technologies
        c.execute('''DELETE FROM projects_project_technologies WHERE project_id=?''', (pid,))
        
        # downloads
        c.execute('''DELETE FROM projects_download WHERE project_id=?''', (pid,))
        
        # descriptions
        c.execute('''SELECT id FROM projects_description WHERE project_id=?''', (pid,))
        dids = [int(data[0]) for data in c.fetchall()]
        c.executemany('''DELETE FROM projects_rawtextdescription WHERE description_ptr_id=?''', dids)
        c.executemany('''DELETE FROM projects_htmlcodedescription WHERE description_ptr_id=?''', dids)
        c.executemany('''DELETE FROM projects_imagedescription WHERE description_ptr_id=?''', dids)
        c.executemany('''DELETE FROM projects_description WHERE id=?''', dids)
        
        # project
        c.execute('''DELETE FROM projects_project WHERE id=?''', (pid,))
        
        conn.commit()
        return True
    return False

