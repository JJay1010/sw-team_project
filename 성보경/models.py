from sqlalchemy.orm import declarative_base, relationship
from connect_db import db

Base = declarative_base()

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.String(10), primary_key=True, nullable=False, unique=True)
    pw = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    type = db.Column(db.Integer, nullable=False) #의료진인지 아닌지


    def __init__(self, user_id, pw, email, type):
        self.user_id = user_id
        self.pw = pw
        self.email = email
        self.type = type


class Animal(db.Model):
    __tablename__ = 'animals'

    animal_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)    
    user_id = db.Column(db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)

    user = db.relationship('User', backref=db.backref('animal_set')) #User의 객체에서 등록된 동물들 참조 가능

    animal_name = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(10), nullable=False) #개 or 고양이
    bday = db.Column(db.String(10))
    sex = db.Column(db.String(10))
    neutered = db.Column(db.String(10))
    weight = db.Column(db.Float)
    image = db.Column(db.String, default="")


    def __init__(self, user, animal_name, type, bday, sex, neutered, weight, image):
        self.user = user
        self.animal_name = animal_name
        self.type = type
        self.bday = bday
        self.sex = sex
        self.neutered = neutered
        self.weight = weight
        self.image = image