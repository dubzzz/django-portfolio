#!/usr/bin/python

import sys
from os import path

__CURRENT_PATH = path.dirname(__file__)

from tornado.web import authenticated
from auth import BaseHandler

sys.path.append(path.join(__CURRENT_PATH, "forms"))
from forms import DummyForm, ProjectHeaderForm

sys.path.append(path.join(__CURRENT_PATH, "..", "models"))
from project import load_project
from project_summary import load_all_summaries, load_summaries_of_year, surround_years, load_categories, load_technologies, create_summary

class HomeHandler(BaseHandler):
    def get(self):
        is_logged = self.is_authentificated()
        form = ProjectHeaderForm(load_categories(), load_technologies()) if is_logged else DummyForm()
        self.render("home.html", STATS=None, by_year_list=load_all_summaries(not is_logged), empty_project_form=form)

class AddProjectHandler(BaseHandler):
    @authenticated
    def post(self):
        form = ProjectHeaderForm(load_categories(), load_technologies())
        data = form.read(self)
        if form.error:
            self.redirect(self.reverse_url('home')) #should maybe render home page with the form
            return
        create_summary(data)
        self.redirect(self.reverse_url('show_project', data['year'], data['name_url']))

class PerYearHandler(BaseHandler):
    def get(self, year):
        projects = load_summaries_of_year(year, not self.is_authentificated())
        prev_year, next_year = surround_years(year, not self.is_authentificated())
        self.render("projects_year.html", projects=projects, year=year, prev_year=prev_year, next_year=next_year)

class ProjectHandler(BaseHandler):
    def get(self, year, project_url):
        project = load_project(year, project_url, not self.is_authentificated())
        if project is None:
            self.redirect(self.reverse_url('error_code', '404'))
            return
        self.render("project.html", project=project)

class ErrorHandler(BaseHandler):
    def get(self, error_code):
        if error_code == "500":
            self.set_status(500)
            self.render("500.html")
        else:
            self.set_status(404)
            self.render("404.html")

