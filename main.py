#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
from google.appengine.ext import db
import auth
import re

USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+.[\S]+$")

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class User(db.Model):
    user_name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def get_by_name(cls, name):
        return User.all().filter('user_name =', name).get()

class MainHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render("posts.html", posts=posts)


class NewPostHandler(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            post = Post(subject=subject, content=content)
            post.put()
            post_id = str(post.key().id())
            self.redirect('/post/%s' % post_id)
        else:
            error = "both subject and content are required"
            self.render("newpost.html", subject=subject, content=content, error=error)


class PostHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        self.render("post.html", post=post)


class SignupHandler(Handler):
    def get(self):
        self.render("signup.html", errors={})

    def post(self):
        user_name = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        errors = {}

        if not USER_RE.match(user_name):
            errors["user"] = "A user name is required"
        else:
            user = User.get_by_name(user_name)
            if user:
                errors["user"] = "user name already exists"

        if not PASSWORD_RE.match(password):
            errors["password"] = "A password is required"
        elif password != verify:
            errors["verify"] = "Passwords do not match"

        if email:
            if not EMAIL_RE.match(email):
                errors["email"] = "An email address is required"

        if errors:
            self.render("signup.html", user_name=user_name, email=email, errors=errors)
        else:
            password_hash = auth.hash_password(password)
            user = User(user_name=user_name, password=password_hash, email=email)
            user.put()
            user_id = str(user.key().id())
            user_hash = auth.make_secure_cookie(user_id)
            self.response.set_cookie("user_id", user_hash)
            self.redirect('/welcome')


class WelcomeHandler(Handler):
    def get(self):
        user_id_param = self.request.cookies.get("user_id")
        user_id = auth.is_valid_cookie(user_id_param)
        if user_id:
            if user_id.isdigit():
                user_id = int(user_id)
                user = User.get_by_id(user_id)
                self.render("welcome.html", user_name=user.user_name)
        else:
            self.redirect("/signup")

class LogInHandler(Handler):
    def get(self):
        self.render("login.html", errors='')

    def post(self):
        user_name = self.request.get("username")
        password = self.request.get("password")
        errors = {}

        if not USER_RE.match(user_name):
            errors["user"] = "User name is not valid"

        if not PASSWORD_RE.match(password):
            errors["password"] = "password is not valid"

        if errors:
            self.render("login.html", errors=errors)
        else:
            user = User.get_by_name(user_name)
            if user:
                if auth.validate_password(password, user.password):
                    self.response.set_cookie("user_id", auth.make_secure_cookie(user.key().id()))
                    self.redirect("/welcome")
                else:
                    errors["password"] = "Passwords do not match"
                    self.render("login.html", errors=errors)
            else:
                errors["user"] = "User Name does not exist"
                self.render("login.html", errors=errors)

class LogOutHandler(Handler):
    def get(self):
        self.response.set_cookie("user_id", '')
        self.redirect("/signup")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewPostHandler),
    ('/post/([0-9]+)', PostHandler),
    ('/signup', SignupHandler),
    ('/welcome', WelcomeHandler),
    ('/login', LogInHandler),
    ('/logout', LogOutHandler)
], debug=True)
