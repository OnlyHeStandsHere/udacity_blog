from blog import BlogHandler
from models.models import Post


class NewPostHandler(BlogHandler):
    def get(self):
        self.render("newpost.html", user=self.user)

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



class PostHandler(BlogHandler):
    def get(self, post_path):
        key = Post.fetch_by_path_id(post_path)
        post = Post.fetch_by_id(key)
        self.render("post.html", post=post)