from flask import Flask, g, session, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# for checklist
from models import User, Animal, Routine, ChecklistDefault, ChecklistRoutine
import datetime
from connect_db import db

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_test.db'
app.config['SECRET_KEY'] = "test"
db.init_app(app)

Migrate(app,db)


@app.route('/', methods=["GET", "POST"])
def checklist():
    # 1. session['login'] 로그인한 유저
    # 2. session['curr_animal'] 관리중인 동물
    session['login'] = 'test'
    session['curr_animal'] = 1


    # checklist db에 저장
    if request.method=="POST":
    
        checks = request.get_json() 
        
        currdate = datetime.datetime.now().date()
        animal_id = checks['animal_id']
        food = checks['food']
        bowels = checks['bowels']
        note = checks['note']

        # multiple routines --> ?
        routine_id = checks['routine_id']
        routine_name = checks['routine_name']
        status = checks['status']

        # model class에 init을 만들면 이렇게 안써도 되긴 함
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
    

    # checklist 열람
    else:
        routines = Routine.query.filter(Routine.animal_id == session['curr_animal']) # 1,2,3,4

        weekdays = ['mon','tue','wed','thu','fri','sat','sun']

        weekly_routines = []

        for weekday in weekdays: 
            lst = []
            for routine in routines:
                if routine.weekday == weekday:
                    lst.append(routine)

            weekly_routines.append(lst)

    return render_template('index.html', routines=routines, weekly_routines=weekly_routines)

if __name__ == "__main__":
    app.run(debug=True)