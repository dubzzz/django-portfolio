import sqlite3
import sys
from os import path

__CURRENT_PATH = path.dirname(__file__)

from project_summary import ProjectSummary

sys.path.append(path.join(__CURRENT_PATH, "..", "scripts"))
from generate_db import DEFAULT_DB

class Project(ProjectSummary):
    def __init__(self, year, name_url, name, short_description, private):
        super(Project, self).__init__(year, name_url, name, short_description, private)
        self.category = None
        self.technologies = list()
        self.modified = None

def project_from_query(data):
    year = data[0]
    name_url = data[1]
    name = data[2]
    short_description = data[3]
    private = data[4]
    return Project(year, name_url, name, short_description, private)

def load_project(year, project_url, private_only):
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        query = '''SELECT year, name_url, name, short_description, private FROM projects_project WHERE year=? AND name_url=?'''
        parameters = (year, project_url,)
        if private_only:
            query += ''' AND private=?'''
            parameters += (False,)
        c.execute(query, parameters)
        
        data = c.fetchone()
        if data is None:
            return None
        
        p = project_from_query(data)
        return p
    return None

