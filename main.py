from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import pymysql

pymysql.install_as_MySQLdb()
import json
from datetime import datetime

with open('config.json', 'r') as c:
    parameters = json.load(c)["parameters"]

local_server = True

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=parameters['gmail-user'],
    MAIL_PASSWORD=parameters['gmail-password']

)
mail = Mail(app)
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = parameters['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = parameters['production_uri']
db = SQLAlchemy(app)


class Contact(db.Model):
    '''serial_no, name, email, phone, message, date '''

    serial_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=True)
    message = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)


class Posts(db.Model):
    '''serial_no, name, email, phone, message, date '''

    serial_no = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=False, nullable=False)
    slug = db.Column(db.String(30), unique=True, nullable=False)
    content = db.Column(db.String(1000), unique=True, nullable=True)
    date = db.Column(db.String(12), unique=False, nullable=True)
    posted_by = db.Column(db.String(30), unique=False, nullable=True)
    subheading = db.Column(db.String(50), unique=False, nullable=True)


@app.route('/')
def home():
    posts = Posts.query.filter_by().all()[0:parameters['number_of_posts']]
    return render_template('index.html', parameters=parameters, posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', parameters=parameters)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if 'user' in session and session['user'] == parameters['admin_username']:
        return render_template('dashboard.html', parameters=parameters)

    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pass')
        if (username == parameters['admin_username'] and password == parameters['admin_password']):
            session['user'] = username
            return render_template('dashboard.html', parameters=parameters)

    return render_template('login.html', parameters=parameters)


@app.route('/post/<string:post_slug>', methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', parameters=parameters, post=post)


@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == 'POST':
        '''Add entry to database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contact(name=name, email=email, phone=phone, message=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message for BSP SANSD from ' + name,
                          sender=email,
                          recipients=[parameters['gmail-user']],
                          body=message + "\n" + phone)

    return render_template('contact.html', parameters=parameters)


if __name__ == '__main__':
    app.run(debug=True)
