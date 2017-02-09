#!/usr/bin/python

import sys
from os import path

__CURRENT_PATH = path.dirname(__file__)

from auth import BaseHandler

sys.path.append(path.join(__CURRENT_PATH, "..", "models"))
from project_summary import load_all_summaries

class HomeHandler(BaseHandler):
    def get(self):
      self.render("home.html", STATS=None, by_year_list=load_all_summaries(self.is_authentificated()))

class PerYearHandler(BaseHandler):
    def get(self, year):
      self.render("base.html")

class ProjectHandler(BaseHandler):
    def get(self, year, project):
      self.render("base.html")

