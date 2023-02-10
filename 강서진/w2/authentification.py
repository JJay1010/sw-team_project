from flask import Flask, request, jsonify, session, Blueprint, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from models import User
from connect_db import db
from sqlalchemy import and_
import json
from flask import flash
import datetime
from sqlalchemy import and_
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash


bp = Blueprint('authetification', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET','POST']) #GET(정보보기), POST(정보수정) 메서드 허용
def register():
    
    if request.method=="POST":
        forms = request.get_json()
        userid = forms['userid']
        email = forms['email']
        password = forms['password']

        user = User(user_id = userid,
                        pw=generate_password_hash(password), email=email
                        )
        #유효성 검사
        check_email = User.query.filter(User.email==email).first()
        check_userid = User.query.filter(User.userid==userid).first()
        
        if check_userid:
            flash("사용 중인 아이디입니다.", category='error')
            return redirect(url_for('register'))
        if check_email:
            flash("이미 가입된 이메일입니다.", category='error')
            return redirect(url_for('register'))


        db.session.add(user)  # id, name 변수에 넣은 회원정보 DB에 저장
        db.session.commit()  #커밋
        flash("가입완료")
        return redirect(url_for('login'))

    

@bp.route('/login', methods=['GET','POST'])  
def login():
    if request.method=="POST":
        forms = request.get_json()
        userid = forms['userid']
        email = forms['email']
        password = forms['password'] 
         #로그인 폼 생성
         #유효성 검사
         
        
        user = User.query.filter(User.user_id == userid).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(userid, password):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['userid'] = userid #form에서 가져온 userid를 session에 저장
            
            return jsonify(forms)
            
        flash(error)
        
        # return redirect('/') #로그인에 성공하면 홈화면으로 redirect
            
    return jsonify(forms) #보류 아마도 animal쪽으로..?

@bp.route('/logout',methods=['GET'])
def logout():
    session.pop('userid',None)
    return redirect(url_for('main'))


@bp.route('/')
def main():
    if 'userid' in session:  # session안에 userid가 있으면 로그인
        return '로그인 성공! 아이디는 %s' % escape(session['userid']) + \
            "<br><a href = '/logout'>로그아웃</a>"

    return "로그인 해주세요. <br><a href = '/login'> 로그인 하러가기! </a>" # 로그인이 안될 경우
