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
    except TypeError: # non-iterable
        lst = []
        objs = objs.__dict__
        del objs['_sa_instance_state']
        lst.append(objs)
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


def update_cr(checklists_routine, json_routines, i):
    routine = json_routines[f'routine{i+1}']

    routine_id = routine['routine_id']
    routine_name = routine['routine_name']
    status = routine['status']

    checklists_routine[i].routine_id = routine_id
    checklists_routine[i].routine_name = routine_name
    checklists_routine[i].status = status
    
    return checklists_routine[i]



@bp.route('/update', methods=["GET", "POST"])
def checklist_update():

    # 임의로 설정한 user & animal, 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1


    # user, animal, today's date, weekday(num)
    current_user = session['login']
    current_animal = session['curr_animal']
    current_date = datetime.datetime.now().date()
    current_weekday_num = str(datetime.datetime.now().weekday())


    if request.method=="GET": # GET
    
        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num)).all()
        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date)).first()
        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == current_animal, 
                                                                ChecklistRoutine.currdate == current_date)).all()
        

        # routine이 없음 
        if routines == []:
            # checklist_default가 있는 경우에만 redirect됨
            checklist_d = query_to_dict(checklist_default)
            
            return jsonify(checklist_d)


        # routine이 있음
        else: 
            # checklist_default, checklist_routine이 이미 있는 경우에 redirect됨
            # # routines, checklist_default와 checklist_routine 반환
            checklist_d = query_to_dict(checklist_default)
            checklist_r = query_to_dict(checklists_routine)
 
            return jsonify(checklist_d, checklist_r)
   

    else: # POST

        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date)).first()
        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == current_animal, 
                                                                ChecklistRoutine.currdate == current_date)).all()                                                        
        
        checks = request.get_json() 
        currdate = datetime.datetime.now().date()
        animal_id = checks['animal_id']

        # checklist_default만 있을 때
        if checklists_routine == []:
            update_cd(checks, checklist_default)
            db.session.commit()      
        
        else:
        # checklist_routine update
            update_cd(checks, checklist_default)
            db.session.commit()  

            json_routines = checks['routines']

            j = 0
            for r in checklists_routine:
                j += 1

            for i in range(j):
                update_cr(checklists_routine, json_routines, i)
                db.session.commit()
    
    return jsonify(checks)


# if __name__ == "__main__":
#     app.run(debug=True)