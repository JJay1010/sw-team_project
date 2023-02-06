from flask import Flask, request, jsonify, session, Blueprint, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from pybo.model import Routine, ChecklistRoutine, ChecklistDefault
from pybo.connect_db import db
import json
import datetime
from sqlalchemy import and_
bp = Blueprint('main', __name__, url_prefix='/')
# current_time = datetime.datetime.now()
# weekday = current_time.weekday()



# @bp.route('/animal', methods=['Post'])
# def animal():
#     param = request.get_json() 
#     session['animal_id'] = param['animal_id'] 
    
#     return jsonify(param) 

#새 루틴 등록
@bp.route('/routine', methods=['POST']) 
def routine():
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

    #json 반환
    return jsonify(param)



#특정 루틴의 체크되어있던 요일 체크 해제 
@bp.route('/weekdaydelete', methods=['POST']) 
def weekdaydelete():
    param = request.get_json() #json: routine_name, animal_id, del_date
    
    #json에서 각 값 임의 변수에 저장
     
    routine_name = param['routine_name']
    animal_id = param['animal_id'] 
    del_date = param['weekday'] #date 부분의 json array를 object로 변환

    


    #루틴 db 삭제
    # for i in range(len(not_routine_date)): #월화목
    del_routine = Routine.query.filter(and_(Routine.animal_id == animal_id, Routine.routine_name==routine_name,
                                                                Routine.weekday == del_date)).first() #체크였다가 체크해제된 row 탐색
        
    del_routine.routine_id
    del_r = Routine.query.get(del_routine.routine_id)
    db.session.delete(del_r)
    db.session.commit()

    #json 반환
    return jsonify(param)


#루틴 수정: 루틴 이름으로 수정은 안되고 아예 해당 루틴을 지우게끔 
@bp.route('/routinedelete', methods=['POST']) 
def routinedelete():
    param = request.get_json() #json: animal_id, routine_name 

    animal_id = param['animal_id']
    routine_name = param['routine_name']

    del_routines = Routine.query.filter(and_(Routine.animal_id == animal_id, Routine.routine_name==routine_name))
                                        
    for del_r in del_routines:
        r = Routine.query.get(del_r.routine_id)
        db.session.delete(r)
        db.session.commit()

    return jsonify(param)

        


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


@bp.route('/checklist', methods=["GET", "POST"])
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
        # 레코드 있을 때 / 없을 때 구분 필요
        # -----------------
    
        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date))
        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == current_animal, 
                                                                ChecklistRoutine.currdate == current_date))
        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num))


        if checklist_default != None or checklists_routine != None:
            return redirect('/update')


        # routine이 있을 시, default 와 routine json 반환
        if routines:
            # 오늘 요일과 일치하는 routine 딕셔너리 리스트
            today_routines = query_to_dict(routines)
            # 오늘 날짜와 일치하는 checklist_default 딕셔너리
            checklist_d = query_to_dict(checklist_default)[0]
            # 오늘 날짜와 일치하는 checklists_routine n개 딕셔너리 
            checklist_r = query_to_dict(checklists_routine)
            return jsonify(today_routines), jsonify(checklist_d), jsonify(checklist_r)
            

        # routine이 없을 시, default 만 반환 (임시로 index.html 설정해놓음)      
        else: 
            checklist_d = query_to_dict(checklist_default)[0]
            return 
   

    else: # POST

        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num))
        
        checks = request.get_json() 

        currdate = datetime.datetime.now().date()
        animal_id = checks['animal_id']
        food = checks['food']
        bowels = checks['bowels']
        note = checks['note']

        json_routines = checks['routines']

        # default checklist
        # # insert
        new_check_d = ChecklistDefault(currdate, animal_id, food, bowels, note)

        db.session.add(new_check_d)

        # checklist_routine
        # query에는 len 못써서 일단 for문 사용
        j = 0
        for r in routines:
            j += 1

        for i in range(j):
            routine = json_routines[f'routine{i+1}']

            routine_id = routine['routine_id']
            routine_name = routine['routine_name']
            status = routine['status']

            new_check_r = ChecklistRoutine(currdate, animal_id, routine_id, routine_name, status)

            db.session.add(new_check_r)
    
        db.session.commit()
    
    return jsonify(checks)




@bp.route('/update', methods=["GET", "POST"])
def checklistupdate():

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
            # 오늘 요일과 일치하는 routine 딕셔너리 리스트
            today_routines = query_to_dict(routines)
            # 오늘 날짜와 일치하는 checklist_default 딕셔너리
            checklist_d = query_to_dict(checklist_default)[0]
            # 오늘 날짜와 일치하는 checklists_routine n개 딕셔너리 
            checklist_r = query_to_dict(checklists_routine)
            db.session.close()
            return jsonify(today_routines), jsonify(checklist_d), jsonify(checklist_r)
            

        # routine이 없을 시, default 만 반환 (임시로 index.html 설정해놓음)      
        else: 
            checklist_d = query_to_dict(checklist_default)[0]
            db.session.close()
        

            return
   

    else: # POST

        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date)).first()
        
        checks = request.get_json() 

        currdate = datetime.datetime.now().date()
        animal_id = checks['animal_id']
        food = checks['food']
        bowels = checks['bowels']
        note = checks['note']

        json_routines = checks['routines']

        checklist_default.food = food
        checklist_default.bowels = bowels
        checklist_default.note = note
        
        db.session.commit()

        # checklist_routine
        # query에는 len 못써서 일단 for문 사용

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

#------------------------------------------------------------------------------------------------------------
# @bp.route('/daily_routine', methods=['GET', 'POST'])
# def daily_routine():
#     if request.method == 'GET':
#         routine = Routine.query.filter(Routine.date=="1").all()
#         for row in routine:
#             checklist_routine = Checklist_routine(animal_id=row.animal_id, routine_name=row.routine_name)
#             db.session.add(checklist_routine)
#             db.session.commit()

#         routines = Checklist_routine.query.all()
        
#         return routines

# @bp.route('/checklist_routine', methods=['GET', 'POST'])
# def checklist_routine():
#    if request.method == 'GET':
#         routines = Routine.query.filter(Routine.animal_id == 1) # 1,2,3,4
#         datas = [dict(id=r.id, checklist_routine = r.checklist_routine) for r in routines]

#         weekdays = ['mon','tue','wed','thu','fri','sat','sun']

#         weekly_routines = []

#         # for weekday in weekdays: 
#         #     lst = [] #요일별로 루틴
#         #     for routine in routines:
#         #         if routine.weekday == weekday:
#         #             lst.append(routine)

#         #     weekly_routines.append(lst) 

#         for weekday in weekdays:
#             for r in routines:
#                 if r.weekday == weekday:
#                     r.checklist_routine.status
        
#         return datas
        
        
        


# if __name__ == "__main__":
#     app.run()
