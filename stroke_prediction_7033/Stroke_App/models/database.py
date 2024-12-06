from flask_sqlalchemy import SQLAlchemy #connects flask app to the database

db = SQLAlchemy() #using SQLalchemy to manaage table

class patients(db.Model): #classes the patient
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    hypertension = db.Column(db.Boolean, default=False)
    heart_disease = db.Column(db.Boolean, default=False)
    ever_married = db.Column(db.Boolean, default=False)
    work_type = db.column(db.Boolean, default=False )
    residence = db.Column(db.Boolean, default=False)
    avg_glucose = db.Column(db.Integer, nullable=False)
    bmi = db.Column(db.String, default=False)
    smoking_status = db.Column(db.String, default=False)
    stroke = db.Column(db.BINARY, default=False)
    stroke = db.Column(db.Boolean, default=False)


    def __repr__(self): #defines how the patient name should be outputted
        return f"<Patient {self.name}>"
