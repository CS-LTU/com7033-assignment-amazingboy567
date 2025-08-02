from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import pandas as pd
import os
import unittest

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# --- MongoDB Setup ---
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["patient_db"]
patient_collection = mongo_db["records"]

# --- User Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# --- Forms ---
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, password=hashed_pw)
        try:
            with app.app_context():
                db.session.add(new_user)
                db.session.commit()
            flash("Registered successfully.", "success")
            return redirect(url_for('login'))
        except:
            flash("Email already registered.", "danger")
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user'] = user.email
            flash("Logged in successfully.", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    patients = list(patient_collection.find({}, {'_id': 0}))
    return render_template('dashboard.html', patients=patients)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out.", "info")
    return redirect(url_for('index'))

# --- Unit Tests ---
class BasicTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

# --- Run App and Load Dataset ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    if patient_collection.estimated_document_count() == 0:
        csv_path = "C:\\Users\\User\\Desktop\\file.csv" 
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            patient_collection.insert_many(df.to_dict(orient='records'))

    app.run(debug=True)


