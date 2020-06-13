from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/bsp'
db = SQLAlchemy(app)


class Contact(db.Model):
    '''serial_no, name, email, phone, message, date '''

    serial_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=True)
    message = db.Column(db.String(120), unique=True, default = 'hi', nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post')
def post():
    return render_template('post.html')


@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == 'POST':
        '''Add entry to database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contact(name=name, email=email, phone=phone, message=message, date = datetime.now())
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html')


app.run(debug=True)
