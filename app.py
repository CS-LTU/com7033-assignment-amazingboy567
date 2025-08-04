from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import pandas as pd
import os #imported os for file path handling
import unittest #imported for unit testing

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
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(), EqualTo('password', message="Passwords must match.")
    ])
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
    return render_template('registration.html', form=form) #incase form has not been submitted/ error shows registration 

@app.route('/login', methods=['GET', 'POST']) #route for user login
def login(): 
    form = LoginForm() #creates custom loginform using FlaskWTF
    if form.validate_on_submit(): #returns true if request method is POST and form data is valid
        user = User.query.filter_by(email=form.email.data).first() #query the database to find user by email
        if user and check_password_hash(user.password, form.password.data): #check_password_hash compares the hashed version with what was entered
            session['user'] = user.email #stores users email in Flask session with a temporary storage
            flash("Logged in successfully.", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid password or email", "Try again")
    return render_template('login.html', form=form) #happens if request method is GET or form is invalid

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: #check is user is logged in
        return redirect(url_for('login')) #prevents access to dashboard if user is not logged in
    patients = list(patient_collection.find({}, {'_id': 0})) #fetches all patient records from MongoDB, excluding the '_id' field
    return render_template('dashboard.html', patients=patients)

@app.route('/logout')
def logout():
    session.pop('user', None) #logs user out by removing their email from the session
    flash("You have successfully been logged out.")
    return redirect(url_for('homepage'))

#Unit tests
class BasicTests(unittest.TestCase):
    def setUp(self): #tells unittest to set up the test environment
        app.config['TESTING'] = True
        self.app = app.test_client() #creates a test client without running a 'real' server

    def test_homepage(self): #simulates GET request to the homepage
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_registration_page(self): #tests the registration page
        response = self.app.get('/registration')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self): #tests the login page
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

#Run App & Load Data
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    if patient_collection.estimated_document_count() == 0: #checks if the collection is empty
        csv_path = r"C:\\Users\\User\\OneDrive\Desktop\\healthcare-dataset-stroke-data.csv" #path to the CSV file
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path) #loads data from CSV file into a pandas DataFrame
            patient_collection.insert_many(df.to_dict(orient='records')) #inserts patient records into MongoDB
            
    app.run(debug=True)
