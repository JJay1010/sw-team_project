from flask_sqlalchemy import SQLAlchemy
import datetime
from connect_db import db
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()
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
    routine_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    animal_id = db.Column(db.Integer, nullable=False)
    routine_name= db.Column(db.String(20), nullable=False)
    weekday = db.Column(db.String(10), nullable=False)

    def __init__(self, routine_id, animal_id, routine_name, weekday):
        self.routine_id = routine_id
        self.animal_id = animal_id
        self.routine_name = routine_name
        self.weekday = weekday


class ChecklistDefault(db.Model):
    __tablename__ = 'checklist_default'

    index = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    currdate = db.Column(db.String(20), nullable=False, default=datetime.datetime.now().date())
    animal_id = db.Column(db.ForeignKey('animals.animal_id'), nullable=False)

    food = db.Column(db.String(10))
    bowels = db.Column(db.String(10))
    note = db.Column(db.String(100))

    def __init__(self, currdate, animal_id, food, bowels, note):
        self.currdate = currdate
        self.animal_id = animal_id
        self.food = food
        self.bowels = bowels
        self.note = note


class ChecklistRoutine(db.Model):
    __tablename__='checklist_routine'

    index = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    routine_id = db.Column(db.ForeignKey('Routine.routine_id'), nullable=False)
    animal_id = db.Column(db.ForeignKey('animals.animal_id'), nullable=False)
    
    currdate = db.Column(db.String(20), nullable=False, default=datetime.datetime.now().date())
    routine_name = db.Column(db.String(20))
    status = db.Column(db.Integer, default="0")

    def __init__(self, currdate, animal_id, routine_id, routine_name, status):
        self.currdate = currdate
        self.animal_id = animal_id
        self.routine_id = routine_id
        self.routine_name = routine_name
        self.status = status


class Journal(db.Model):
    __tablename__ = 'journal'

    index = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    animal_id = db.Column(db.ForeignKey('animals.animal_id'), nullable=False)
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False)

    title = db.Column(db.String)
    image = db.Column(db.String)
    content = db.Column(db.String)
    currdate = db.Column(db.String(10))

    def __init__(self, animal_id, user_id, title, image, content, currdate):
        self.animal_id = animal_id
        self.user_id = user_id
        self.title = title
        self.image = image
        self.content = content
        self.currdate = currdate


class Health(db.Model):
    __tablename__ = 'health'

    index = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    animal_id = db.Column(db.ForeignKey('animals.animal_id'), nullable=False)
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False)

    title = db.Column(db.String)
    image = db.Column(db.String, default="")
    comment = db.Column(db.String)
    currdate = db.Column(db.String(10))

    def __init__(self, animal_id, user_id, title, image, comment, currdate):
        self.animal_id = animal_id
        self.user_id = user_id
        self.title = title
        self.image = image
        self.comment = comment
        self.currdate = currdate
