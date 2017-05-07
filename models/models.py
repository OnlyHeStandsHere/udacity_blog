from google.appengine.ext import db
from helpers import app


class User(db.Model):
    user_name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def fetch_by_name(cls, name):
        return User.all().filter('user_name =', name).get()

    @classmethod
    def fetch_by_id(cls, key):
        return cls.get_by_id(key)

    @classmethod
    def fetch_by_user_id_cookie(cls, user_cookie):
        user_id = user_cookie.split('|')[0]
        if user_id.isdigit():
            user_id = int(user_id)
            user = User.fetch_by_id(user_id)
            if user:
                return user

    @classmethod
    def log_in(cls, user_name, password):
        user = cls.fetch_by_name(user_name)
        if user and app.validate_password(password, user.password):
            return user


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def fetch_by_path_id(cls, post_path):
        return db.Key.from_path('Post', int(post_path))

    @classmethod
    def fetch_by_id(cls, key):
        return db.get(key)
