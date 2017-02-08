from tornado.web import RequestHandler

import hashlib
import sqlite3
import sys
from os import path

__CURRENT_PATH = path.dirname(__file__)

sys.path.append(path.join(__CURRENT_PATH, "..", "scripts"))
from generate_db import DEFAULT_DB

class BaseHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")

class LoginHandler(BaseHandler):
    def get(self):
        try:
            nextpage = self.request.arguments["next"][0].decode('utf_8')
        except (KeyError, IndexError) as e:
            nextpage = "/"
        self.render("login.html", page="login", nextpage=nextpage)

    def post(self):
        try:
            nextpage = self.request.arguments["next"][0].decode('utf_8')
        except (KeyError, IndexError) as e:
            nextpage = "/"
        try:
            username = self.request.arguments["username"][0].decode('utf_8')
        except (KeyError, IndexError) as e:
            self.render("login.html", page="login", nextpage=nextpage)
            return
        try:
            password = self.request.arguments["password"][0].decode('utf_8')
        except (KeyError, IndexError) as e:
            self.render("login.html", page="login", nextpage=nextpage)
            return

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

        self.render("login.html", page="login", nextpage=nextpage)

class LogoutHandler(BaseHandler):
    def get(self):
        username = self.current_user
        self.clear_cookie("username")
        self.render("logout.html", page="login", username=username)

