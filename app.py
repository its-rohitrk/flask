import datetime

from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
import json
import os
from werkzeug.utils import secure_filename


with open('config.json','r') as c:

    parms = json.load(c)["parms"]

local_server=True
app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config['UPLOAD_FOLDER']=parms["location"]


#app.config.update(
   # MAIL_SERVER = 'smtp.gmail.com',
   # MAIL_PORT = '465',
   # MAIL_USE_SSL = True,
   # MAIL_USERNAME = parms['user'],
   # MAIL_PASSWORD = parms['pass']
#)
#mail = Mail(app)


if local_server:
    app.config['SQLALCHEMY_DATABASE_URI']= parms['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI']= parms['prod_uri']




#app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:@localhost/codeninja'
db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    message = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20))

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(50), nullable=False, unique=True)
    img_file = db.Column(db.String(20), nullable=True)
    date = db.Column(db.String(20))




@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:parms['no_posts']]
    return render_template('index.html',parms=parms, posts = posts)


@app.route("/post/<string:post_slug>",methods=['GET','POST'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug = post_slug).first()
    return render_template('post.html',parms=parms,post=post)


@app.route("/about")
def about():
    return render_template('about.html',parms=parms)

@app.route("/dashbord",methods = ['GET','POST'])
def dashbord():
    if ('user' in session and session['user']==parms['admin_user']):
        posts = Posts.query.all()
        return render_template('dashbord.html',parms=parms,posts=posts)
    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username==parms['admin_user'] and userpass==parms['password']):
            session['user']=username
            posts = Posts.query.all()
            return render_template('dashbord.html', parms=parms,posts = posts)


    return render_template('login.html',parms=parms)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if "user" in session and session['user'] == parms['admin_user']:
        if request.method == "POST":
            title = request.form.get('title')
            #tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.datetime.now()

            if sno == '0':
                post = Posts(title=title, slug=slug, content=content,img_file = img_file,date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.box_title = title

                #post.tline = tline
                post.slug = slug

                post.content = content

                #post.img_file = img_file
                #post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)

    #post = Posts.query.filter_by(sno=sno).first()
    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html', parms=parms, post=post)

@app.route("/uploder",methods = ['GET','POST'])
def uploder():
    if "user" in session and session['user'] == parms['admin_user']:
        if request.method == "POST":
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "upload succesfully!"

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashbord')

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if "user" in session and session['user'] == parms['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashbord')


@app.route("/contact",methods = ['GET','POST'])
def contact():
    if (request.method)=='POST':
        #sno= request.form.get('')
        name= request.form.get('name')
        contact= request.form.get('phone')
        email= request.form.get('email')
        message= request.form.get('message')
        entry = Contacts(name=name,email=email,contact=contact,message=message,date = datetime.datetime.now())
        print(entry)
        db.session.add(entry)
        db.session.commit()
        # email sent code
        #mail.send_message('new message',
                         # sender=email,
                        #  recipients=[parms["user"]],
                         # body = message + "\n" + name

 #       )
    return render_template('contact.html',parms=parms)
app.run(debug=True)
