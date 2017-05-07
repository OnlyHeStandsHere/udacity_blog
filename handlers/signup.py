from blog import BlogHandler, USER_RE, PASSWORD_RE, EMAIL_RE
from models.models import User
from helpers import app


class SignupHandler(BlogHandler):
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
            user = User.fetch_by_name(user_name)
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
            password_hash = app.hash_password(password)
            user = User(user_name=user_name, password=password_hash, email=email)
            user.put()
            user_id = str(user.key().id())
            user_hash = app.make_secure_cookie(user_id)
            self.response.set_cookie("user_id", user_hash)
            self.redirect('/welcome')


