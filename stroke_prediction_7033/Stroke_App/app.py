from flask import Flask, render_template, request, redirect, url_for, flash
from models.database import db, Patient
from wtforms import Form, StringField, IntegerField, BooleanField, SelectField
from wtforms.validators import InputRequired, NumberRange, ValidationError
import re

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create a form for patient registration
class PatientForm(Form):
    name = StringField('Name', validators=[InputRequired()])
    age = IntegerField('Age', validators=[InputRequired(), NumberRange(min=0)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    hypertension = BooleanField('Hypertension')
    heart_disease = BooleanField('Heart Disease')
    stroke = BooleanField('Stroke')

    # Custom validation for name field
    def validate_name(form, field):
        if not re.match("^[A-Za-z ]+$", field.data):
            raise ValidationError("Name must contain only letters and spaces")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = PatientForm(request.form)
    if request.method == 'POST' and form.validate():
        # Create a new patient record and save to database
        patient = Patient(
            name=form.name.data,
            age=form.age.data,
            gender=form.gender.data,
            hypertension=form.hypertension.data,
            heart_disease=form.heart_disease.data,
            ever_married=form.ever_married.data,
            work_type=form.work_type.data,
            residence=form.residence.data,
            avg_glucose=form.avg_glucose.data,
            bmi=form.bmi.data,
            smoking_status=form.smoking_status.data,
            stroke=form.stroke.data

        )
        db.session.add(patient)
        db.session.commit()
        flash("Patient registered successfully!", "success")
        return redirect(url_for('patients'))
    return render_template('register.html', form=form)

@app.route('/patients')
def patients():
    # Retrieve all patients from the database
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

if __name__ == "__main__":
    app.run(debug=True)


with app.app_context():
    db.create_all()
    print("Database and tables have been initialized.")

