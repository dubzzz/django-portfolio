#!/usr/bin/python

from auth import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
      self.render("base.html", page="home")

