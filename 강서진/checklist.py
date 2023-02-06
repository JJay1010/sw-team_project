from flask import Flask, g, session, request, jsonify, render_template, redirect, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_migrate import Migrate

import update

# for checklist
from models import Routine, ChecklistDefault, ChecklistRoutine
import datetime
from connect_db import db
import json

app = Flask(__name__)

app.register_blueprint(update.bp)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_test.db'
app.config['SECRET_KEY'] = "test"
db.init_app(app)

Migrate(app,db)


# -----------------
# from number to weekday
# -----------------
# def to_weekday(num):
#     weekdays = ['mon','tue','wed','thu','fri','sat','sun']
#     num = int(num)
#     return weekdays[num]

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
# json to ckl_d
# -----------------
def json_to_new_cd(js):
    currdate = datetime.datetime.now().date()
    animal_id = js['animal_id']
    food = js['food']
    bowels = js['bowels']
    note = js['note']

    new_check_d = ChecklistDefault(currdate, animal_id, food, bowels, note)

    return new_check_d


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
        # -----------------
        # checklist 레코드 있을 때 update로 리다이렉트
        # -----------------
    
        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date))
        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == current_animal, 
                                                                ChecklistRoutine.currdate == current_date))
        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num))


        if checklist_default != None:
            return redirect('/update')

        elif checklists_routine != None:
            return redirect('/update')

        # routine이 있을 시, default 와 routine json 반환
        if routines:
            today_routines = query_to_dict(routines)
            checklist_d = query_to_dict(checklist_default)[0]
 
            checklist_r = query_to_dict(checklists_routine)
            return jsonify(today_routines), jsonify(checklist_d), jsonify(checklist_r)

        # routine이 없을 시, default 만 반환
        else: 
            checklist_d = query_to_dict(checklist_default)[0]
            return jsonify(checklist_d)
   

    else: # POST

        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num))
        checks = request.get_json() 
        json_routines = checks['routines']

        # default checklist insert
        new_cd = json_to_new_cd(checks)
        db.session.add(new_cd)

        # routine checklist insert
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