from flask import Flask, session, request, jsonify, render_template, redirect
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from markupsafe import escape
from flask_bcrypt import Bcrypt

import os
from models import User
from connect_db import db
from forms import RegisterForm, LoginForm

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_test.db'
app.config['SECRET_KEY'] = "test"
app.config['BCRYPT_LEVEL'] = 10

db.init_app(app)
Migrate(app,db)
bcrypt = Bcrypt(app)

@app.route('/register', methods=['GET','POST']) #GET(정보보기), POST(정보수정) 메서드 허용
def register():
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

if __name__ == "__main__":
    app.run(debug=True)

