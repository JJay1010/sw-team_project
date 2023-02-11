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

        user = User(user_id = user_id, pw=pw, email=email)

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
        password = forms['pw']

         #유효성 검사
        user = User.query.filter(User.user_id == user_id).first()

        if not user:
            return "error - user not in db"
        
        elif not check_password_hash(user.pw, password):
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

    return redirect(url_for('authentification.login')) # 로그인이 안된 경우


@bp.route('/register_animal', methods=['GET','POST'])
def register_animal():
    try:
        session['login'] = request.headers['user_id']

    # 로그인 x시 로그인 창으로 리다이렉트
    except:
        if 'user_id' not in session:
            return redirect('authentification.main')

    param = request.get_json()

    if request.method=="GET":
        return "animal registration form"
               
        
    else: # POST
        user = User.query.filter_by(user_id = session['login']).first()
        
        animal_name = param['animal_name']
        bday = param['bday']
        sex = param['sex']
        neutered = param['neutered']
        weight = param['weight']

        animal = Animal(user = user, animal_name=animal_name, bday=bday, sex=sex, neutered=neutered, weight=weight)

        db.session.add(animal)
        db.session.commit()

        curr_animal = Animal.query.filter(and_(Animal.user_id == session['login'],
                                            Animal.animal_name == animal_name)).first()

        curr_animal = curr_animal.__dict__
        del curr_animal['_sa_instance_state']

        return jsonify(curr_animal)
        # 등록된 동물 정보 json 반환, 이 뒤로 header에 animal_id 주고받기
