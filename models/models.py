from google.appengine.ext import db


class User(db.Model):
    user_name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def fetch_by_name(cls, name):
        return User.all().filter('user_name =', name).get()

    @classmethod
    def fetch_by_id(cls, key):
        return db.get(key)


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
