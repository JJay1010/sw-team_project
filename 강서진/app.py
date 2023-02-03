from flask import Flask, g, session, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# for checklist
from models import User, Animal, Routine, ChecklistDefault, ChecklistRoutine
import datetime
from connect_db import db
import json
import pandas as pd

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_test.db'
app.config['SECRET_KEY'] = "test"
db.init_app(app)

Migrate(app,db)

# -----------------
# from number to weekday
# -----------------
def to_weekday(num):
    weekdays = ['mon','tue','wed','thu','fri','sat','sun']
    num = int(num)
    return weekdays[num]




@app.route('/', methods=["GET", "POST"])
def checklist():
    # 1. session['login'] 로그인한 유저
    # 2. session['curr_animal'] 관리중인 동물
    session['login'] = 'test'
    session['curr_animal'] = 1


    # checklist db에 저장
    # 0. 오늘 처음 기록 -- checklist_default, checklist_routines 오늘 날짜 비어있으면 전부 add
    # 1. 기록 수정 및 추가 -- 오늘 날짜 비어있는 부분에만 add, 나머지는 update?
    if request.method=="POST":
    
        checks = request.get_json() 
        
        currdate = datetime.datetime.now().date()
        animal_id = checks['animal_id']
        food = checks['food']
        bowels = checks['bowels']
        note = checks['note']

        # uhh multiple routines --> will probably numbered?

        routine_id = checks['routine_id']
        routine_name = checks['routine_name']
        status = checks['status']

        checklist_default = ChecklistDefault() 
        checklist_default.currdate = currdate
        checklist_default.animal_id = animal_id
        checklist_default.food = food
        checklist_default.bowels = bowels
        checklist_default.note = note
        
        checklist_routine = ChecklistRoutine()
        checklist_routine.currdate = currdate
        checklist_routine.animal_id = animal_id
        checklist_routine.routine_id = routine_id
        checklist_routine.routine_name = routine_name
        checklist_routine.status = status

        
        db.session.add(checklist_default)
        db.session.add(checklist_routine)

        db.session.commit()
        
        return jsonify(checks)
    

    else: # GET

        # 0. 설정한 routine이 없을 때 -- default만 표시
        # 0-0. 완전 처음 사용해서 routine도, default 기록도 없을 때
        # 1. 오늘 처음 기록 입력시 -- 오늘의 routines json 반환
        # 2. 기록 수정 + 추가 -- checklist_default, checklist_routines json 반환

        checklists_default = ChecklistDefault.query.filter(ChecklistDefault.animal_id == session['curr_animal'])
        checklists_routine = ChecklistRoutine.query.filter(ChecklistRoutine.animal_id == session['curr_animal'])
        routines = Routine.query.filter(Routine.animal_id == session['curr_animal'])

        if routines == None:
            print("no routines")

        if checklists_default == None:
            print("no default checklist")

        for checklist_default in checklists_default:
            if checklist_default.currdate == str(datetime.datetime.now().date()):
                checklist_default = checklist_default.__dict__
                del checklist_default['_sa_instance_state']





        # 1. 
        today_weekday = str(datetime.datetime.now().weekday()) # 4

        

        today_lst = []
        for routine in routines:
            if routine.weekday == today_weekday:
                routine = routine.__dict__
                del routine['_sa_instance_state']
                today_lst.append(routine)

        # for lst in today_lst:
            # lst 형태는 {'animal_id': 1, 'routine_name': 'teeth', 'routine_id': 4, 'weekday': '4'}, dict
             # 4 = fri


    return         

if __name__ == "__main__":
    app.run(debug=True)