#새 루틴 등록
from flask import Flask, request, jsonify, session, Blueprint, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from pybo.model import Routine, ChecklistRoutine, ChecklistDefault, User
from pybo.connect_db import db
import json
import boto3
import requests
from flask import flash
import datetime
from sqlalchemy import and_
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

def query_to_dict(objs):
    try:
        lst = []
        for obj in objs:
            obj = obj.__dict__
            del obj['_sa_instance_state']
            lst.append(obj)
        return lst
    except TypeError: # non-iterable
        lst = []
        objs = objs.__dict__
        del objs['_sa_instance_state']
        lst.append(objs)
        return lst
    
bp = Blueprint('routine', __name__, url_prefix='/routine')
@bp.route('/routine', methods=['GET','POST']) 
def routine():
    
    session['animal_id'] = 1
    animal_id = session['animal_id']
    
    if request.method=="POST": #루틴 등록
        param = request.get_json() #json: animal_id, routine_name, date:{mon=true,tue=true...}, 
    
        #json에서 각 값 임의 변수에 저장
     
        routine_name = param['routine_name']
        animal_id = param['animal_id']

     
        date_dict = param['weekday'] #date 부분의 json array를 object로 변환
        routine_date = [] #월수금
        for key, val in date_dict.items():
            if val=='true':
                routine_date.append(key) #true인 요일값들 저장


        #모델로 routine 객체 만들기
        for i in range(len(routine_date)): #월, 수, 금 3개 저장
            routine = Routine(animal_id=animal_id, routine_name=routine_name, weekday=routine_date[i]) 
            #db에 저장, 업데이트
            db.session.add(routine)
            db.session.commit()

    
        return redirect(url_for('routine.routine'))
    
    else: #get 루틴 불러오기
        # param = request.get_json() #json: animal_id, routine_name, date:{mon=true,tue=true...}, 
    
        #json에서 각 값 임의 변수에 저장
     
        
        # animal_id = param['animal_id']
        routines = Routine.query.filter(Routine.animal_id==animal_id).all()
        routines = query_to_dict(routines)
        return jsonify(routines)





#특정 루틴의 체크되어있던 요일 체크 해제 
@bp.route('/weekdaydelete', methods=['POST']) 
def weekdaydelete():
    param = request.get_json() #json: routine_name, animal_id, weekday
    
    #json에서 각 값 임의 변수에 저장
     
    routine_name = param['routine_name']
    animal_id = param['animal_id'] 
    del_date = param['weekday'] #date 부분의 json array를 object로 변환

    


    #루틴 db 삭제
    # for i in range(len(not_routine_date)): #월화목
    del_routine = Routine.query.filter(and_(Routine.animal_id == animal_id, Routine.routine_name==routine_name,
                                                                Routine.weekday == del_date)).first() #체크였다가 체크해제된 row 탐색
        
    
    del_r = Routine.query.get(del_routine.routine_id)
    db.session.delete(del_r)
    db.session.commit()

    #json 반환
    return jsonify(param)


#루틴 수정: 루틴 이름으로 수정은 안되고 아예 해당 루틴을 지우게끔 
@bp.route('/routinedelete', methods=['POST']) 
def routinedelete():
    param = request.get_json() #json:  animal_id, routine_name

    animal_id = param['animal_id']
    routine_name = param['routine_name']

    del_routines = Routine.query.filter(and_(Routine.animal_id == animal_id, Routine.routine_name==routine_name))
                                        
    for del_r in del_routines:
        r = Routine.query.get(del_r.routine_id)
        db.session.delete(r)
        db.session.commit()

    return jsonify(param)
