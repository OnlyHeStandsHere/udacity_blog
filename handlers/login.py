from models.models import User
from blog import BlogHandler, USER_RE, PASSWORD_RE


class LogInHandler(BlogHandler):
    def get(self):
        self.render("login.html", errors='')

    def post(self):
        user_name = self.request.get("username")
        password = self.request.get("password")
        errors = {}

        if not USER_RE.match(user_name):
            errors["user"] = "Please enter a valid user name"

        if not PASSWORD_RE.match(password):
            errors["password"] = "Please enter a valid password"

        if errors:
            self.render("login.html", errors=errors)
        else:
            user = User.log_in(user_name, password)
            if user:
                self.set_secure_cookie("user_id", user.key().id())
                self.redirect("/welcome")


class LogOutHandler(BlogHandler):
    def get(self):
        self.response.set_cookie("user_id", "")
        self.redirect("/")
