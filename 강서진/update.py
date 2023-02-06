from flask import Flask, g, session, request, jsonify, render_template, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_migrate import Migrate

# for checklist
from models import Routine, ChecklistDefault, ChecklistRoutine
import datetime
from connect_db import db
import json

bp = Blueprint('update', __name__, url_prefix='/')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_test.db'
# app.config['SECRET_KEY'] = "test"
# db.init_app(app)

# Migrate(app,db)


# -----------------
# from number to weekday
# -----------------
def to_weekday(num):
    weekdays = ['mon','tue','wed','thu','fri','sat','sun']
    num = int(num)
    return weekdays[num]

# -----------------
# from db.query to dictionary (in list)
# -----------------
def query_to_dict(objs):
    lst = []
    for obj in objs:
        obj = obj.__dict__
        del obj['_sa_instance_state']
        lst.append(obj)
    return lst


# -----------------
# update checklist_default
# -----------------
def update_cd(js, record):
    food = js['food']
    bowels = js['bowels']
    note = js['note']

    record.food = food
    record.bowels = bowels
    record.note = note

    return record


# -----------------
# update checklist_routine
# -----------------
# def update_cr(js, record):


@bp.route('/update', methods=["GET", "POST"])
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
        # 레코드 있을 때 / 없을 때 구분 필요
    
        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date))
        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == current_animal, 
                                                                ChecklistRoutine.currdate == current_date))
        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num))


        # routine이 있을 시, default 와 routine json 반환
        if routines:

            today_routines = query_to_dict(routines)
            checklist_d = query_to_dict(checklist_default)[0]
            checklist_r = query_to_dict(checklists_routine)
            db.session.close()
            return jsonify(today_routines), jsonify(checklist_d), jsonify(checklist_r)

        # routine이 없을 시, default 만 반환 
        else: 
            checklist_d = query_to_dict(checklist_default)[0]
            db.session.close()

            return jsonify(checklist_d)
   

    else: # POST

        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date)).first()
        
        checks = request.get_json() 
        currdate = datetime.datetime.now().date()
        animal_id = checks['animal_id']
        
        # checklist default update
        update_cd(checks, checklist_default)
        
        db.session.commit()

        # checklist_routine update
        json_routines = checks['routines']
        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == current_animal, 
                                                                ChecklistRoutine.currdate == current_date)).all()

        j = 0
        for r in checklists_routine:
            j += 1

        for i in range(j):
            routine = json_routines[f'routine{i+1}']

            routine_id = routine['routine_id']
            routine_name = routine['routine_name']
            status = routine['status']

            checklists_routine[i].routine_id = routine_id
            checklists_routine[i].routine_name = routine_name
            checklists_routine[i].status = status

            db.session.commit()
    
    return jsonify(checks)


# if __name__ == "__main__":
#     app.run(debug=True)