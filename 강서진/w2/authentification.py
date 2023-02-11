from flask import Flask, request, jsonify, session, Blueprint, url_for, redirect
from models import User, Animal
from connect_db import db
from sqlalchemy import and_
from flask import flash
from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash


bp = Blueprint('authentification', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET','POST']) #GET(정보보기), POST(정보수정) 메서드 허용
def register():

    if request.method=="POST":
        forms = request.get_json()

        user_id = forms['user_id']
        pw = generate_password_hash(forms['pw'])
        email = forms['email']

        user = User(user_id = user_id, password=pw, email=email)

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
        db.session.commit()  #커밋

        return redirect(url_for('authentification.login'))

    else: # GET
        return "registration form"


@bp.route('/login', methods=['GET','POST'])  
def login():
    if request.method=="POST":

        forms = request.get_json()

        user_id = forms['user_id']
        password = forms['password']

         #유효성 검사
        user = User.query.filter(User.user_id == user_id).first()

        if not user:
            return "error - user not in db"
        
        elif not check_password_hash(user.password, password):
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

    except:
        if 'user_id' not in session:
            return redirect('authentification.main')

    else:
        if request.method=="POST":

            user = User.query.filter_by(user_id = session['login']).first()
            
            animal_name = param['animal_name']
            bday = param['bday']
            sex = param['sex']
            neutered = param['neutered']
            weight = param['weight']

            animal = Animal(user = user, animal_name=animal_name, bday=bday, sex=sex, neutered=neutered, weight=weight)

            db.session.add(animal)
            db.session.commit()

            # 등록 후 세션에 동물 id 등록해야



            return "animal registered"
            
        else: # GET
            return "animal registration form"

        