import sqlite3
import sys
from datetime import datetime
from os import path

__CURRENT_PATH = path.dirname(__file__)

sys.path.append(path.join(__CURRENT_PATH, "..", "scripts"))
from generate_db import DEFAULT_DB

class ProjectSummary(object):
    def __init__(self, year, name_url, name, short_description, private):
        self.year = year
        self.name_url = name_url
        self.name = name
        self.short_description = short_description
        self.private = private

def project_from_query(data):
    year = data[0]
    name_url = data[1]
    name = data[2]
    short_description = data[3]
    private = data[4]
    return ProjectSummary(year, name_url, name, short_description, private)

def load_all_summaries(private_only):
    year_mapping = dict()
    projects_by_year = list();
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        if private_only:
            c.execute('''SELECT year, name_url, name, short_description, private FROM projects_project WHERE private=?''', (False,))
        else:
            c.execute('''SELECT year, name_url, name, short_description, private FROM projects_project''')
        for data in c.fetchall():
            p = project_from_query(data)
            if p.year not in year_mapping:
                year_mapping[p.year] = len(projects_by_year)
                projects_by_year.append((p.year, list(),))
            
            projects_by_year[year_mapping[p.year]][1].append(p)
    
    return sorted(projects_by_year, key=lambda projects: projects[0], reverse=True)

def load_summaries_of_year(year, private_only):
    projects = list();
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        if private_only:
            c.execute('''SELECT year, name_url, name, short_description, private FROM projects_project WHERE year=? AND private=?''', (year, False,))
        else:
            c.execute('''SELECT year, name_url, name, short_description, private FROM projects_project WHERE year=?''', (year,))
        for data in c.fetchall():
            projects.append(project_from_query(data))
    return projects

def surround_years(year, private_only):
    prev_year, next_year = None, None
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        if private_only:
            c.execute('''SELECT MAX(year) as prev_year, NULL as next_year FROM projects_project WHERE year<? AND private=? UNION SELECT NULL as prev_year, MIN(year) as next_year FROM projects_project WHERE year>? AND private=?''', (year, False, year, False))
        else:
            c.execute('''SELECT MAX(year) as prev_year, NULL as next_year FROM projects_project WHERE year<? UNION SELECT NULL as prev_year, MIN(year) as next_year FROM projects_project WHERE year>?''', (year,year,))
        for data in c.fetchall():
            if data[0] is not None:
                prev_year = data[0]
            if data[1] is not None:
                next_year = data[1]
    return (prev_year, next_year)

def load_categories():
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        c.execute('''SELECT id, name FROM projects_category ORDER BY name''')
        return [(str(data[0]), data[1]) for data in c.fetchall()]
    return []

def load_technologies():
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        c.execute('''SELECT id, name FROM projects_technology ORDER BY name''')
        return [(str(data[0]), data[1]) for data in c.fetchall()]
    return []

def create_summary(data):
    creation_time = datetime.now()
    with sqlite3.connect(DEFAULT_DB) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO projects_project(name, name_url, short_description, year, private, category_id, created, modified) VALUES(?,?,?,?,?,?,?,?)''',
            (data["name"], data["name_url"], data["short_description"], int(data["year"]), data["private"], int(data["category"]), creation_time, creation_time,))
        rid = c.lastrowid
        c.executemany('''INSERT INTO projects_project_technologies(project_id, technology_id) VALUES(?,?)''', [(rid, int(techid)) for techid in data["technologies"]])
        conn.commit()

