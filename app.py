from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import pandas as pd
import os #imported os for file path handling
import unittest  #imported for unit testing

#initialise flask app and sql databse
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

#MongoDB Set Up
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["patient_db"]
patient_collection = mongo_db["records"]

#The model used for the user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

#forms for registration and login
#registration form for new users and login form for existing users
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    submit = SubmitField('Register')

#login form for existing users
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

#Routes for application pages
@app.route('/')
def homepage():
    return render_template('homepage.html') #render_template is used for all pages to render HTML templates for the specific route

@app.route('/registration', methods=['GET', 'POST']) #get & post are the HTTP methods this route accepts. 'GET' load the form, 'Post' submits the form.
def registration():
    form = RegisterForm() #uses FlaskWTF
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data) #converts plain password to hashed format using Werkzeug
        new_user = User(email=form.email.data, password=hashed_pw) #creates new user
        try:
            with app.app_context(): #ensures new user is added to the database and in the flask app context
                db.session.add(new_user)
                db.session.commit()
            flash("Registration complete")
            return redirect(url_for('login'))
        except:
            flash("Email already registered.", "try a different email") #shows error message
    return render_template('registration.html', form=form) #incase form has not been submitted/ error shows registration form




