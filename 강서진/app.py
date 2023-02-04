from flask import Flask, g, session, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_migrate import Migrate

# for checklist
from models import Routine, ChecklistDefault, ChecklistRoutine
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
        # 레코드 있을 때 / 없을 때 구분 필요
    
        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date))
        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == current_animal, 
                                                                ChecklistRoutine.currdate == current_date))
        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num))


        # routine이 없을 시, default 만 반환 (임시로 index.html 설정해놓음)
        if routines == None:
            checklist_d = query_to_dict(checklist_default)[0]
            return render_template('index.html', checklist_d=checklist_d)


        # routine이 있을 시, default 와 routine json 반환
        else: 
            # 오늘 요일과 일치하는 routine 딕셔너리 리스트
            today_routines = query_to_dict(routines)
            # 오늘 날짜와 일치하는 checklist_default 딕셔너리
            checklist_d = query_to_dict(checklist_default)[0]
            # 오늘 날짜와 일치하는 checklists_routine n개 딕셔너리 
            checklist_r = query_to_dict(checklists_routine)
            return render_template('index.html', routines=jsonify(today_routines), checklist_d=jsonify(checklist_d), checklist_r=jsonify(checklist_r))
   

    else:   # POST
        checks = request.get_json() 

        # json 안에 json, key값 임의로 설정

        # checks
        # ----------------
        # {
        #     "currdate":"2023-02-05",
        #     "animal_id":1,
        #     "food":"45g",
        #     "bowels":"정상",
        #     "note":NULL,

        #     "routines":
        #     {
        #         "routine1":
        #         {
        #             "routine_id":7,
        #             "routine_name":"med",
        #             "status": None
        #         },
        #         "routine2":
        #         {
        #             "routine_id":8,
        #             "routine_name":"nail",
        #             "status":1
        #         }
        #     }
        # }


        # default checklist
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

        db.session.add(checklist_default)


        # routine checklist
        # ------------------
        # 루틴 1개 이상       
        # 오늘 설정된 routine 개수만큼 ChecklistRoutine 객체 생성하여 db 세션에 add
        # ------------------
        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num))
        
        json_routines = checks['routines']

        
        # query에는 len 못써서 일단 for문 사용
        j = 0
        for routine in routines:
            j += 1

        for i in range(j):
            routine = json_routines[f'routine{i+1}']
            routine_id = routine['routine_id']
            routine_name = routine['routine_name']
            status = routine['status']

            checklist_routine = ChecklistRoutine()
            checklist_routine.currdate = currdate
            checklist_routine.animal_id = animal_id
            checklist_routine.routine_id = routine_id
            checklist_routine.routine_name = routine_name
            checklist_routine.status = status
            
            db.session.add(checklist_routine)
        
        db.session.commit()
        
        return render_template('index.html', checks = jsonify(checks))
    


if __name__ == "__main__":
    app.run(debug=True)
