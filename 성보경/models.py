from flask_sqlalchemy import SQLAlchemy
#db = SQLAlchemy()           #SQLAlchemy를 사용해 데이터베이스 저장
from connect_db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model): 
    __tablename__ = 'user'   #테이블 이름 : user
    email = db.Column(db.String(32), unique=True, nullable=False)
    userid = db.Column(db.String(32), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(8), nullable=False)


    # def __init__(self, userid, email, password, **kwargs):
    #   self.userid = userid
    #   self.email = email
 
    #   self.set_password(password)


    def set_password(self, password):
        self.password = generate_password_hash(password)
 
    def check_password(self, password):
        return check_password_hash(self.password, password)