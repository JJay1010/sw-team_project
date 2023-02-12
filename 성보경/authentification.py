from flask import Flask, request, jsonify, session, Blueprint, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from models import User, Animal
from connect_db import db
from sqlalchemy import and_
import json
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('authentification', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET','POST'])
def register():
    pw = "12341234@"
    print(generate_password_hash(pw))

    if request.method=="POST":
        forms = request.get_json()

        user_id = forms['user_id']
        pw = generate_password_hash(forms['pw'])
        email = forms['email']
        type = forms['type']

        user = User(user_id=user_id, pw=pw, email=email, type=type)

        # 중복 검사
        check_email = User.query.filter(User.email==email).first()
        check_userid = User.query.filter(User.user_id==user_id).first()
        
        if check_userid:
            # flash("사용 중인 아이디입니다.", category='error')

            return redirect(url_for('authentification.register'))

        if check_email:
            # flash("이미 가입된 이메일입니다.", category='error')
            return redirect(url_for('authentification.register'))

        db.session.add(user)  # id, pw(hash), email 변수에 넣은 회원정보 DB에 저장
        db.session.commit()   #커밋

        return redirect(url_for('authentification.login'))

    else: # GET
        return "registration form"


@bp.route('/withdrawal', methods=['DELETE'])
def withdrawal():
    user = User.query.filter_by(user_id=session['user_id']).first()

    db.session.delete(user)
    db.session.commit()

    return "Withdrawal SUCCESS"


@bp.route('/login', methods=['GET','POST'])  
def login():
    if request.method=="POST":

        forms = request.get_json()

        user_id = forms['user_id']
        pw = forms['pw']

         #유효성 검사
        user = User.query.filter(User.user_id == user_id).first()

        if not user:
            return "error - user not in db"
        
        elif not check_password_hash(user.pw, pw):
            return "error - wrong pw"

        else:
            session.clear()
            session['user_id'] = user_id #form에서 가져온 user_id를 session에 저장
            
            return f"{session['user_id']} logged in"
        
        # return  #로그인에 성공하면 홈화면으로 redirect
    
    else: # GET
        return "login form"


@bp.route('/logout',methods=['GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('authentification.main'))


@bp.route('/', methods=["GET"])
def main():
    if 'user_id' in session:  # session안에 user_id가 있으면 로그인
        return f"{session['user_id']} is logged in"

    return "not logged in" # 로그인이 안된 경우


@bp.route('/register_animal', methods=['GET','POST'])
def register_animal():
    param = request.get_json()

    try:
        session['login'] = request.headers['user_id']

    # 로그인 x시 로그인 창으로 리다이렉트
    except:
        if 'user_id' not in session:
            return redirect('authentification.main')

    if request.method=="GET":
        print(session['login'])
        return "animal registration form"

    else:
    
        user = User.query.filter_by(user_id=session['user_id']).first()
        animal_name = param['animal_name']
        type = param['type']
        bday = param['bday']
        sex = param['sex']
        neutered = param['neutered']
        weight = param['weight']
        image = param['image']

        animal = Animal(user=user, animal_name=animal_name, type=type, bday=bday, sex=sex, neutered=neutered, weight=weight, image=image) #relationship에 user 객체 넘겨주기

        db.session.add(animal)
        db.session.commit()

        return "animal registered"

# @bp.route('/user_pw_edit', methods=['GET', 'POST'])
# def user_pw_edit():
#     if request.method=="POST":
#         forms = request.get_json()
#         new_pw = generate_password_hash(forms['pw']) #새로운 비밀번호 받아오기

#         user = User.query.filter_by(user_id=session['user_id']).first() #로그인된 유저의 객체 가져오기
#         user.pw = new_pw #비밀번호 변경

#         db.session.add(user)
#         db.session.commit()

#         return "EDIT PW FORM"
#     else:
#         return "EDIT PW SUCCESS"

# @bp.route('/user_email_edit', methods=['GET', 'POST'])
# def user_email_edit():
    if request.method=="POST":
        forms = request.get_json()
        new_email = forms['email']

        user = User.query.filter_by(user_id=session['user_id']).first()
        user.email = new_email

        db.session.add(user)
        db.session.commit()

        return "EDIT EMAIL SUCCESS"
    else:
        return "EDIT EMAIL FORM"


