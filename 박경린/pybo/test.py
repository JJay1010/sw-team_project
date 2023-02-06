from flask import Flask, request, jsonify, session, Blueprint
from flask_sqlalchemy import SQLAlchemy
from pybo.model import Routine, ChecklistRoutine
from pybo.connect_db import db
import json
import datetime
from sqlalchemy import and_
bp = Blueprint('main', __name__, url_prefix='/')
# current_time = datetime.datetime.now()
# weekday = current_time.weekday()
weekday = 1


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

     
    date_dict = param['date'] #date 부분의 json array를 object로 변환
    routine_date = [] #월수금
    for key, val in date_dict.items():
        if val=='true':
            routine_date.append(key) #true인 요일값들 저장


    #모델로 routine 객체 만들기
    for i in range(len(routine_date)): #월, 수, 금 3개 저장
        routine = Routine(animal_id=animal_id, routine_name=routine_name, date=routine_date[i]) 
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
    del_date = param['date'] #date 부분의 json array를 object로 변환

    


    #루틴 db 삭제
    # for i in range(len(not_routine_date)): #월화목
    del_routine = Routine.query.filter(and_(Routine.animal_id == animal_id, Routine.routine_name==routine_name,
                                                                Routine.date == del_date)).first() #체크였다가 체크해제된 row 탐색
        
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
