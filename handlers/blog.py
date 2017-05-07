import jinja2
import webapp2
import os
from helpers import app
from models.models import User
import re

USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+.[\S]+$")



template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def get_user_cookie(self):
        user_cookie = self.request.cookies.get("user_id")
        if app.validate_cookie(user_cookie):
            return user_cookie

    def set_secure_cookie(self, name, value):
        cookie = app.make_secure_cookie(value)
        self.response.set_cookie(name, cookie)

    def initialize(self, *args, **kwargs):
        webapp2.RequestHandler.initialize(self, *args, **kwargs)
        user_id = self.get_user_cookie()
        if user_id:
            self.user = User.fetch_by_user_id_cookie(user_id)

class HomeHandler(BlogHandler):
    def get(self):
        self.render("home.html")


class WelcomeHandler(BlogHandler):
    def get(self):
        user_cookie = self.get_user_cookie()
        if user_cookie:
            user = User.fetch_by_user_id_cookie(user_cookie)
            if user:
                self.render("welcome.html", user_name=user.user_name)
            else:
                self.redirect("/signup")
        else:
            self.redirect("/signup")