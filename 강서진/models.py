from flask_sqlalchemy import SQLAlchemy
from datetime import date
from connect_db import db
# db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.String(10), primary_key=True, nullable=False, unique=True)
    pw = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)

    def __init__(self, user_id, username, pw, email):
        self.user_id = user_id
        self.username = username
        self.pw = pw
        self.email = email


class Animal(db.Model):
    __tablename__ = 'animals'

    animal_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)    
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False)
    animal_name = db.Column(db.String(10), nullable=False)
    bday = db.Column(db.String(10))
    sex = db.Column(db.String(10))
    neutered = db.Column(db.String(10))
    weight = db.Column(db.Float)

    def __init__(self, animal_id, user_id, animal_name, bday, sex, neutered, weight):
        self.animal_id = animal_id
        self.user_id = user_id
        self.animal_name = animal_name
        self.bday = bday
        self.sex = sex
        self.neutered = neutered
        self.weight = weight


class Routine(db.Model):
    __tablename__= 'Routine'
    routine_id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, nullable=False)
    # animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'))
    routine_name= db.Column(db.String(20), nullable=False)
    weekday = db.Column(db.String(10), nullable=False)


class ChecklistDefault(db.Model):
    __tablename__ = 'checklist_default'

    index = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    currdate = db.Column(db.DateTime, nullable=False, unique=True, default=date.today())
    animal_id = db.Column(db.ForeignKey('animals.animal_id'), nullable=False)

    food = db.Column(db.String(10))
    bowels = db.Column(db.String(10))
    note = db.Column(db.String(100))


class ChecklistRoutine(db.Model):
    __tablename__='checklist_routine'

    index = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    currdate = db.Column(db.DateTime, nullable=False, unique=True, default=date.today())
    animal_id = db.Column(db.ForeignKey('animals.animal_id'), nullable=False)
    routine_id = db.Column(db.ForeignKey('Routine.routine_id'), nullable=False)
    routine_name = db.Column(db.String(20), nullable=False)
    status = db.Column(db.Integer, nullable=False)
