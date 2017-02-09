import sqlite3
import sys
from os import path

__CURRENT_PATH = path.dirname(__file__)

sys.path.append(path.join(__CURRENT_PATH, "..", "scripts"))
from generate_db import DEFAULT_DB

class ProjectSummary:
    def __init__(self, year, name_url, name, short_description, private):
        self.year = year
        self.name_url = name_url
        self.name = name
        self.short_description = short_description
        self.private = private

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
            year = data[0]
            name_url = data[1]
            name = data[2]
            short_description = data[3]
            private = data[4]
            
            if year not in year_mapping:
                year_mapping[year] = len(projects_by_year)
                projects_by_year.append((year, list(),))
            
            projects_by_year[year_mapping[year]][1].append(ProjectSummary(year, name_url, name, short_description, private))
    
    return sorted(projects_by_year, key=lambda projects: projects[0], reverse=True)

