from flask import Flask, g, session, request, jsonify, render_template
# from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3

# for checklist
from models import User, Animal, Routine, ChecklistDefault, ChecklistRoutine
from datetime import date
from connect_db import db

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_test.db'
app.config['SECRET_KEY'] = "test"
db.init_app(app)

Migrate(app,db)


# @bp.route('/routine', methods=['POST']) 
# def routine():
#     checks = request.get_json() #json받기
    
#     #json에서 각 값 임의 변수에 저장
#     routine_id = checks['routine_id'] 
#     routine_name = checks['routine_name']
#     date = checks['date']
#     animal_id = checks['animal_id']

#     #모델로 routine 객체 만들기 
#     routine = Routine(routine_id=routine_id, animal_id=animal_id, routine_name=routine_name, date=date) 

#     #db에 저장, 업데이트
#     db.session.add(routine)
#     db.session.commit()

#     #json 반환
#     return jsonify(checks)


@app.route('/', methods=["GET", "POST"])
def checklist():
    # 1. session['login']
    # 2. session['curr_animal']
    # 3. session['routine_id']
    session['login'] = 'test'
    session['curr_animal'] = 1

    routines = Routine.query.filter(Routine.animal_id ==session['curr_animal'])

    # checklist 입력된 값 db에 저장
    checks = request.get_json() 
    
    currdate = date.today()
    animal_id = checks['animal_id']
    food = checks['food']
    bowels = checks['bowels']
    note = checks['note']
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



if __name__ == "__main__":
    app.run(debug=True)