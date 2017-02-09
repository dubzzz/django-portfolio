from tornado.web import RequestHandler

import hashlib
import sqlite3
import sys
from os import path

__CURRENT_PATH = path.dirname(__file__)

sys.path.append(path.join(__CURRENT_PATH, "forms"))
from forms import LoginForm

sys.path.append(path.join(__CURRENT_PATH, ".."))
from config import HEADER_ADMIN, HEADER_GPLUS, HEADER_QUICKLINKS, FOOTER_TEXT, FOOTER_QUICKLINKS, THEME, STATS

sys.path.append(path.join(__CURRENT_PATH, "..", "scripts"))
from generate_db import DEFAULT_DB

class BaseHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")
    def render(self, filename, **kwargs):
        kwargs["HEADER_ADMIN"] = HEADER_ADMIN
        kwargs["HEADER_GPLUS"] = HEADER_GPLUS
        kwargs["HEADER_QUICKLINKS"] = HEADER_QUICKLINKS
        kwargs["FOOTER_TEXT"] = FOOTER_TEXT
        kwargs["FOOTER_QUICKLINKS"] = FOOTER_QUICKLINKS
        kwargs["THEME"] = THEME
        kwargs["AUTHENTIFICATED"] = self.get_current_user() != None and self.get_current_user() != ""
        kwargs["AUTHENTIFICATED_USERNAME"] = self.get_current_user()
        return super(BaseHandler, self).render(filename, **kwargs)

class LoginHandler(BaseHandler):
    def get(self):
        try:
            nextpage = self.request.arguments["next"][0].decode('utf_8')
        except (KeyError, IndexError) as e:
            nextpage = "/"
        self.render("login.html", page="login", nextpage=nextpage, form=LoginForm())

    def post(self):
        try:
            nextpage = self.request.arguments["next"][0].decode('utf_8')
        except (KeyError, IndexError) as e:
            nextpage = "/"
        
        loginform = LoginForm()
        data = loginform.read(self)
        if loginform.error:
            self.render("login.html", page="login", nextpage=nextpage, form=loginform)
            return
        
        username = data["username"]
        password = data["password"]
        
        conn = sqlite3.connect(DEFAULT_DB)
        with conn:
            c = conn.cursor()
            c.execute('''SELECT username, password, salt FROM users WHERE username=? LIMIT 1''', (username,))
            data = c.fetchone()
            if data is not None:
                h = hashlib.sha1()
                h.update(data[2]+password)
                hashvalue = unicode(h.hexdigest())
                if hashvalue == data[1]:
                    self.set_secure_cookie("username", username)
                    self.redirect(nextpage)
                    return
        
        loginform.error = True
        self.render("login.html", page="login", nextpage=nextpage, form=loginform)

class LogoutHandler(BaseHandler):
    def get(self):
        username = self.current_user
        self.clear_cookie("username")
        self.render("logout.html", page="login", username=username)

