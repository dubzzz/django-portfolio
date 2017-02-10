#!/usr/bin/python

import sys
from os import path

__CURRENT_PATH = path.dirname(__file__)

from auth import BaseHandler

sys.path.append(path.join(__CURRENT_PATH, "..", "models"))
from project import load_project
from project_summary import load_all_summaries, load_summaries_of_year, surround_years

class HomeHandler(BaseHandler):
    def get(self):
        self.render("home.html", STATS=None, by_year_list=load_all_summaries(not self.is_authentificated()))

class PerYearHandler(BaseHandler):
    def get(self, year):
        projects = load_summaries_of_year(year, not self.is_authentificated())
        prev_year, next_year = surround_years(year, not self.is_authentificated())
        self.render("projects_year.html", projects=projects, year=year, prev_year=prev_year, next_year=next_year)

class ProjectHandler(BaseHandler):
    def get(self, year, project_url):
        project = load_project(year, project_url, not self.is_authentificated())
        self.render("project.html", project=project)

class ErrorHandler(BaseHandler):
    def get(self, error_code):
        if error_code == "500":
            self.set_status(500)
            self.render("500.html")
        else:
            self.set_status(404)
            self.render("404.html")

