from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://blogz:blogzz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self. password = password

@app.before_request
def require_login():
    allowed_routes = ['log_on', 'register', 'index', 'blog_index', 'sign_validate']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/home')
def index():
    users = User.query.all()
    
    template = jinja_env.get_template('home.html')
    return template.render(users=users)
@app.route('/blog')
def blog_index():
    blog_id = request.args.get('id')
    blog_user = request.args.get('user')
    
    if not blog_id and not blog_user:
        blogss = Blog.query.all()
        userss = User.query.all()
        template = jinja_env.get_template('all_blogs.html')
        return template.render(blogss=blogss, userss=userss)
    elif blog_id:
        the_entry = Blog.query.get(blog_id)
        the_user = the_entry.owner
        # the_user = User.query.filter_by(id = b_owner).first()

        template = jinja_env.get_template('a_blog.html')
        #return template.render(entry = the_entry, a_user= the_user)
        return template.render(entry = the_entry, a_user = the_user)
    else:
        #the_user = User.query.get(blog_user)
        #the_id = the_user.self
        #blogss = Blog.query.get(the_id)
        #user_blogs = Blog.query.all(the_id)
        a_user = User.query.filter_by(id = blog_user).first()
        user_blogs = Blog.query.filter_by(owner = a_user).all()
        template = jinja_env.get_template('a_user.html')
        return template.render(blogss=user_blogs, the_user = a_user)

@app.route('/newpost')
def newblog():
    template = jinja_env.get_template('new_post.html')
    return template.render(failed_title='', title_error='', failed_body='', body_error='')
@app.route('/newpost', methods=['POST'])
def newblog_validate():
    owner = User.query.filter_by(username=session['username']).first()
    title = request.form['new_title']
    body = request.form['new_body']
    title_error=''
    body_error=''
    if not title:
        title_error="Please enter a title for your blog."
    if not body:
        body_error="Please enter a body for your blog."
    if not title_error and not body_error:
        new_blog = Blog(title, body, owner)   
        db.session.add(new_blog)
        db.session.commit()
        a_user = new_blog.owner
        template = jinja_env.get_template('a_blog.html')
        return template.render(entry = new_blog, a_user = a_user)
    else:
        template = jinja_env.get_template('new_post.html')
        return template.render(failed_title=title, title_error=title_error, failed_body=body, body_error=body_error)



#@app.route('/login', methods=['POST', 'GET'])
#def login():
#    if request.method == 'POST':
#        name = request.form['login_name']
#        the_pass = request.form['login_password']
#        login_error=''
#       logpass_error=''
#        user = User.query.filter_by(username=name).first()
#        if not name:
#            login_error="Please enter your username."
#        if not the_pass:
#            logpass_error="Please enter your password."
#        if not login_error and not logpass_error:
#            if user and user.password == the_pass:
#                session['username'] = name
#                return redirect('/')
#            else:
#                login_error="Incorrect username or password."
#                template = jinja_env.get_template('login.html')
#                return template.render(failed_login=name, login_error=login_error, failed_logpass=the_pass, logpass_error=logpass_error)
#        else:
#            template = jinja_env.get_template('login.html')
#            return template.render(failed_login=name, login_error=login_error, failed_logpass=the_pass, logpass_error=logpass_error)


@app.route('/login')
def log_on():
    template = jinja_env.get_template('login.html')
    return template.render(failed_login='', login_error='', failed_logpass='', logpass_error='')
@app.route('/login', methods=['POST'])
def login_validate():
    name = request.form['login_name']
    the_pass = request.form['login_password']
    login_error=''
    logpass_error=''
    user = User.query.filter_by(username=name).first()

    if not name:
        login_error="Please enter your username."
    if not the_pass:
        logpass_error="Please enter your password."
    if not login_error and not logpass_error:
        if user: 
            if user.password == the_pass:
                session['username'] = name
                return redirect('/newpost')
            else:
                logpass_error = "Incorrect password."
                template = jinja_env.get_template('login.html')
                return template.render(failed_login=name, login_error=login_error, failed_logpass=the_pass, logpass_error=logpass_error)
        else:
            login_error="Invalid username."
            template = jinja_env.get_template('login.html')
            return template.render(failed_login=name, login_error=login_error, failed_logpass=the_pass, logpass_error=logpass_error)
        #template = jinja_env.get_template('success.html')
        #return template.render()
    else:
        template = jinja_env.get_template('login.html')
        return template.render(failed_login=name, login_error=login_error, failed_logpass=the_pass, logpass_error=logpass_error)
@app.route('/logout')
def delete_user():
    #if session['username']:
    del session['username']
    return redirect('/blog')
    

@app.route('/sign_up')
def register():
    template = jinja_env.get_template('signup.html')
    return template.render(failed_name='', name_error='', failed_password='', password_error='', verify_error='')
@app.route('/sign_up', methods=['POST'])
def sign_validate():
    user_name = request.form['reg_username']
    pass_word = request.form['reg_password']
    verify = request.form['ver_password']
    name_error=''
    password_error=''
    verify_error=''
    if not user_name:
        name_error="Please enter a username."
    if not pass_word:
        password_error="Please enter a password."
    if not verify:
        verify_error="Please verify your password."
    if pass_word != verify:
        verify_error = "Passwords do not match."
    if len(user_name) > 0 and len(user_name) < 3:
        name_error = "Not a valid username."
    if len(pass_word) > 0 and len(pass_word) < 3:
        password_error = "Not a valid password."
    xist = User.query.filter_by(username = user_name).first()
    if xist:
        name_error = "User already exists."
    if not name_error and not password_error and not verify_error:

        new_user = User(user_name, pass_word)
        db.session.add(new_user)
        db.session.commit()
        #return redirect('/')
        session['username'] = user_name
        return redirect('/newpost')
    else:
        template = jinja_env.get_template('signup.html')
        return template.render(failed_name=user_name, name_error= name_error, failed_password=pass_word, password_error=password_error, verify_error=verify_error)

if __name__ == '__main__':
    app.run()