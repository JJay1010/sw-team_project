from flask import Flask, g, session, request, jsonify, render_template, redirect, Blueprint, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_migrate import Migrate

import update
import journal

# for checklist
from models import Routine, ChecklistDefault, ChecklistRoutine
import datetime
from connect_db import db
import json

app = Flask(__name__)

app.register_blueprint(update.bp)
app.register_blueprint(journal.bp)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_test.db'
app.config['SECRET_KEY'] = "test"
db.init_app(app)

Migrate(app,db)


# -----------------
# from db.query to dictionary (in list)
# -----------------
def query_to_dict(objs):
    try:
        lst = []
        for obj in objs:
            obj = obj.__dict__
            del obj['_sa_instance_state']
            lst.append(obj)
        return lst
    except TypeError:
        return None


# -----------------
# json to ckl_d
# -----------------
def json_to_new_cd(js):
    currdate = datetime.datetime.now().date()
    animal_id = js['animal_id']
    food = js['food']
    bowels = js['bowels']
    note = js['note']

    new_cd = ChecklistDefault(currdate, animal_id, food, bowels, note)

    return new_cd


# ----------------
# json to ckl_r
# ----------------
def json_to_new_cr(animal_id, routine):
    currdate = datetime.datetime.now().date()
    animal_id = animal_id
    routine_id = routine['routine_id']
    routine_name = routine['routine_name']
    status = routine['status']

    new_cr = ChecklistRoutine(currdate, animal_id, routine_id, routine_name, status)

    return new_cr


@app.route('/checklist', methods=["GET", "POST"])
def checklist():

    # 임의로 설정한 user & animal, 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1


    # user, animal, today's date, weekday(num)
    current_user = session['login']
    current_animal = session['curr_animal']
    current_date = datetime.datetime.now().date()
    current_weekday_num = str(datetime.datetime.now().weekday())


    if request.method=="GET": # GET
    
        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date)).first()
        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == current_animal, 
                                                                ChecklistRoutine.currdate == current_date)).all()
        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num)).all()


        # routine이 없음 --> default만 
        if routines == []:
            # checklist_default 기록이 있음 --> 수정으로 넘어감
            if checklist_default != None:
                return redirect(url_for('update.checklist_update'))

            # checklist_default 기록이 없음 --> 입력 폼만 반환
            else: 
                return "checklist_default form"


        # routine이 있음 --> default와 routine 둘 다
        else: 
            # checklist_default 기록이 있음 
            # (== 자동으로 checklist_routine 기록도 있음) --> 수정으로 넘어감
            if checklist_default != None:
                # today_routines = query_to_dict(routines)
                # checklist_d = query_to_dict(checklist_default)
                # checklist_r = query_to_dict(checklists_routine)
                return redirect(url_for('update.checklist_update'))

            # checklist_default, checklist_routine 기록이 없음 --> routine json, 입력 폼 반환
            else:
                today_routines = query_to_dict(routines)
                return jsonify(today_routines)
   

    else: # POST

        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num)).all()
        checks = request.get_json() 

        # 기록된 routine이 없음 --> checklist_default만 기록
        if routines == []:
            new_cd = json_to_new_cd(checks)
            db.session.add(new_cd)

        # 기록된 routine이 있음 --> checklist_default와 checklist_routine 기록
        else:
            json_routines = checks['routines']

            new_cd = json_to_new_cd(checks)
            db.session.add(new_cd)

            j = 0
            for r in routines:
                j += 1

            for i in range(j):
                routine = json_routines[f'routine{i+1}']
                new_cr = json_to_new_cr(checks['animal_id'], routine)
                db.session.add(new_cr)      
        
        db.session.commit()

    return jsonify(checks)        


if __name__ == "__main__":
    app.run(debug=True)