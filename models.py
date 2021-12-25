from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class User(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    hashed_pass = db.Column(db.Text, nullable=False)
    national_id = db.Column(db.String(15), unique=True)


class Doctor(User):
    def to_dict(self):
        vals = vars(self)
        return {attr: vals[attr] for attr in vals if 'instance_state' not in attr}


class Patient(User):
    def to_dict(self):
        vals = vars(self)
        return {attr: vals[attr] for attr in vals if 'instance_state' not in attr}


class Admin(db.Model):
    username = db.Column(db.String(15), primary_key=True)
    hashed_pass = db.Column(db.Text, nullable=False)

    def to_dict(self):
        vals = vars(self)
        return {attr: vals[attr] for attr in vals if 'instance_state' not in attr}
