from flask import Flask, g, session, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_migrate import Migrate

# for checklist
from models import User, Animal, Routine, ChecklistDefault, ChecklistRoutine
import datetime
from connect_db import db
import json


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




@app.route('/checklist', methods=["GET", "POST"])
def checklist():
    session['login'] = 'test'
    session['curr_animal'] = 1

    if request.method=="GET": # GET

        # 1. 오늘 처음 기록 입력시 -- 오늘의 routines json 반환
        # 2. 기록 수정 + 추가 -- checklist_default, checklist_routines json 반환

        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == session['curr_animal'], 
                                                                ChecklistDefault.currdate == datetime.datetime.now().date()))

        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == session['curr_animal'], 
                                                                ChecklistRoutine.currdate == datetime.datetime.now().date()))

        routines = Routine.query.filter(and_(Routine.animal_id == session['curr_animal'], Routine.weekday == str(datetime.datetime.now().weekday())))

        # routine이 없을 시, default 폼만 반환
        if routines == None:
            return render_template('index.html')


        # routine이 있을 시, default 폼에 routine json 반환

        else: 

            # 오늘 요일과 일치하는 routine 딕셔너리를 리스트에 넣어 리턴
            today_routines = []
            for routine in routines:
                routine = routine.__dict__
                del routine['_sa_instance_state']
                today_routines.append(routine)


            # 오늘 날짜와 일치하는 checklist_default 1개 레코드 반환 
            for checklist_d in checklist_default:
                checklist_d = checklist_d.__dict__
                del checklist_d['_sa_instance_state']


            # 오늘 날짜와 일치하는 checklists_routine n개 리스트에 넣어 반환
            today_checklist_r = []
            for checklist_r in checklists_routine:
                checklist_r = checklist_r.__dict__
                del checklist_r['_sa_instance_state']
                today_checklist_r.append(checklist_r)


            print(today_checklist_r)

            jchecklist = jsonify(checklist_d)
            print(type(jchecklist)) # <class 'flask.wrappers.Response'>


            return render_template('index.html', routines=jsonify(today_routines), checklist=jsonify(checklist_d), checklist_r=jsonify(today_checklist_r))
   

    # checklist db에 저장
    # 기록 저장
    else:   # POST
    
        checks = request.get_json() 

        # default box
        currdate = datetime.datetime.now().date()
        animal_id = checks['animal_id']
        food = checks['food']
        bowels = checks['bowels']
        note = checks['note']

        checklist_default = ChecklistDefault() 
        checklist_default.currdate = currdate
        checklist_default.animal_id = animal_id
        checklist_default.food = food
        checklist_default.bowels = bowels
        checklist_default.note = note


        # routine box
        # ------------------
        # 루틴이 1개 이상일 때는? 
        # ------------------
        routine_id = checks['routine_id']
        routine_name = checks['routine_name']
        status = checks['status']

        
        checklist_routine = ChecklistRoutine()
        checklist_routine.currdate = currdate
        checklist_routine.animal_id = animal_id
        checklist_routine.routine_id = routine_id
        checklist_routine.routine_name = routine_name
        checklist_routine.status = status

        
        db.session.add(checklist_default)
        db.session.add(checklist_routine)

        db.session.commit()
        
        return render_template('checkform.html', checks = jsonify(checks))
    


if __name__ == "__main__":
    app.run(debug=True)