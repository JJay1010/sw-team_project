from flask import Flask, session, request, jsonify, render_template, redirect
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from markupsafe import escape
from flask_bcrypt import Bcrypt

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from models import User, Animal
from connect_db import db
from forms import RegisterForm, LoginForm

app = Flask(__name__)

WTF_CSRF_ENABLED = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_test.db'
app.config['SECRET_KEY'] = "test"
app.config['BCRYPT_LEVEL'] = 10

db.init_app(app)
Migrate(app,db)
bcrypt = Bcrypt(app)

@app.route('/register', methods=['GET','POST'])
def register_User():
    forms = RegisterForm()
    if forms.validate_on_submit():
        user = User()
        user.userid = forms.data.get('userid')
        user.email = forms.data.get('email')
        user.set_password(forms.data.get('password'))

        #유효성 검사
        check_email = User.query.filter_by(email=user.email).first()
        check_userid = User.query.filter_by(userid=user.userid).first()
        
        if check_userid:
            flash("사용 중인 아이디입니다.", category='error')
            return render_template('register.html', forms=forms)
        if check_email:
            flash("이미 가입된 이메일입니다.", category='error')
            return render_template('register.html', forms=forms)

        print(user.userid,user.password)  
        db.session.add(user)  # id, name 변수에 넣은 회원정보 DB에 저장
        db.session.commit()  #커밋
        flash("가입완료")
        return redirect('/')
    return render_template('register.html', forms=forms)

@app.route('/login', methods=['GET','POST'])  
def login():  
    forms = LoginForm() #로그인 폼 생성
    if forms.validate_on_submit(): #유효성 검사
        session['userid'] = forms.data.get('userid') #form에서 가져온 userid를 session에 저장
        flash("환영합니다.")
    
        return redirect('/') #로그인에 성공하면 홈화면으로 redirect
            
    return render_template('login.html', forms=forms)

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('userid',None)
    return redirect('/')

@app.route('/')
def main():
    if 'userid' in session:  # session안에 userid가 있으면 로그인
        return '로그인 성공! 아이디는 %s' % escape(session['userid']) + \
            "<br><a href = '/logout'>로그아웃</a>"

    return "로그인 해주세요. <br><a href = '/login'> 로그인 하러가기! </a>" # 로그인이 안될 경우

@app.route('/registerAnimal', methods=['GET','POST'])
def register_animal():
    param = request.get_json()

    if 'userid' not in session:
        return redirect('/')
    else:
        #userid = session['userid'] #세션에 저장된 id값 받아오기

        user = User.query.filter_by(userid='test').first() #속성 userid가 userid와 동일한 객체 가져오기

        animal = Animal(user = user) #relationship에 user 객체 넘겨주기

        animal.animal_name = param['animal_name']
        animal.bday = param['bday']
        animal.sex = param['sex']
        animal.neutered = param['neutered']
        animal.weight = param['weight']

        db.session.add(animal)
        db.session.commit()
        flash("등록이 완료되었습니다.")

    return jsonify(param) 

if __name__ == "__main__":
    app.run(debug=True)

