from flask_sqlalchemy import SQLAlchemy
from connect_db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model): 
    __tablename__ = 'user'   #테이블 이름 : user
    email = db.Column(db.String(32), unique=True, nullable=False)
    userid = db.Column(db.String(32), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(8), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
 
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Animal(db.Model):
    __tablename__='animal'
    animal_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(), db.ForeignKey('user.userid', ondelete='CASCADE')) #사용자 삭제 시 동물도 삭제
    user = db.relationship('User', backref=db.backref('animal_set')) #User의 객체에서 등록된 동물들 참조 가능
    #routines = db.relationship('Routine')
    
    animal_name = db.Column(db.String(20), nullable=False)
    bday = db.Column(db.String(6), nullable=True)
    sex = db.Column(db.String(), nullable=True)
    neutered = db.Column(db.String(), nullable=True)
    weight = db.Column(db.Float, nullable=True)