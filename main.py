from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:junglebook@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

'''
-- Main page displays multiple posts. Clicking on a post redirects you to a page showing the 
post title and body. The URL for this page contains a query parameter with the id of the blog post.

-- Uses the nav link to go to the /newpost page and creates a new post. Check for error handling (if either 
body or title is empty, you should get a user error). Submitting a valid post redirects you 
to the post’s individual entry page rather than the main home page.

-- Returning to the main page (/blog) should show the new post at the bottom of the list.

'''

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

class User(db.Model):                                        # set up the user data base
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):                  # initialize user data
        self.username = username
        self.password = password

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog')
def blog():
    blog_id = request.args.get('id')

    if blog_id == None:
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts, title='Build-a-blog')
    else:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post, title='Blog Entry')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Please enter a blog entry"

        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Entry')

@app.route('/logout')    # for logout routine
def logout():
    del session['username']
    return redirect('/blog') 

if  __name__ == "__main__":
    app.run()