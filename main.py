from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:junglebook@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "mF7%z9LWw4$zj20a"


class Blog(db.Model):                                             # set up the blog data base
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, pub_date=None):        # initialize blog data
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.owner = owner
        
class User(db.Model):                                        # set up the user data base
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):                  # initialize user data
        self.username = username
        self.password = password

@app.before_request
def require_login():                                          # Allowed route list
    allowed_routes = ['login', 'signup', 'index', 'blog']             
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
    
@app.route('/')
def index():
    users = Blog.query.all()
    return render_template('index.html', users=users, header='Blog Users')

@app.route('/blog')                          # For blog listing
def blog():

    
    posts = Blog.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    
    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id)
        return render_template('user.html', posts=posts, header="User Posts")
    if blog_id:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post )

    return render_template('blog.html', posts=posts, header='All Blog Posts')

@app.route('/newpost', methods=['POST', 'GET'])              # For new blog post page
def new_post(): 
    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        title_error = ''
        body_error = ''

        if not blog_title:                                     # check for errors
            title_error = "Please enter a new blog title"
        if not blog_body:
            body_error = "Please enter some blog entry"

        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body, owner)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', header='New Blog Entry', title_error=title_error, 
                body_error=body_error, blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', header='New Blog Entry')

@app.route('/login', methods=['POST', 'GET'])           # For /login page
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']

        login_error = ''
        login = ''

        user = User.query.filter_by(username=username).first()      #if no user, user == None
        
        if user and user.password == password:                      
            session['username'] = username
            login = 'User Logged in'
            
            return render_template('newpost.html', login=login) 
        else:                                                        # check for login error
            login_error = 'Username and/or password is incorrect, or does not exist'
            return render_template('login.html', header='Login', login_error = login_error)
    
    return render_template('login.html', header='Login')

@app.route('/signup', methods=['POST', 'GET'])        # For /signup page
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        length_error = ''
        password_error = ''
        user_error = ''

        existing_user = User.query.filter_by(username=username).first()
        

        if existing_user:                                      # check for duplicate user
            user_error = 'User already exists'
        elif len(username) < 3 or len(password) < 3:            # check for minimum length
            length_error = 'Username and/or password must be more than 3 characters'
        elif password != verify:                                  #check for password error
            password_error = 'Password does not match'
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
                                                                #check for user, password, length error
        return render_template('signup.html', header='Signup', user_error=user_error, length_error=length_error, 
                password_error=password_error)   

    return render_template('signup.html', header='Signup')

@app.route('/logout')    # for logout routine
def logout():
    del session['username']
    return redirect('/blog') 

if  __name__ == "__main__":
    app.run()