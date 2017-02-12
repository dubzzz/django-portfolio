import sqlite3
import sys
from datetime import datetime
from os import path

__CURRENT_PATH = path.dirname(__file__)

from project_summary import ProjectSummary

sys.path.append(path.join(__CURRENT_PATH, "..", "scripts"))
from generate_db import DEFAULT_DB

class Project(ProjectSummary):
    def __init__(self, year, name_url, name, short_description, private, modified, category):
        super(Project, self).__init__(year, name_url, name, short_description, private)
        self.category = category
        self.technologies = list()
        self.modified = modified

def project_from_query(data):
    year = data[0]
    name_url = data[1]
    name = data[2]
    short_description = data[3]
    private = data[4]
    modified = data[5]
    category = data[6]
    return Project(year, name_url, name, short_description, private, modified, category)

def load_project(year, project_url, private_only):
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        query = '''SELECT proj.year, proj.name_url, proj.name, proj.short_description, proj.private, proj.modified, cat.name
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
        
        p = project_from_query(data)
        return p
    return None

