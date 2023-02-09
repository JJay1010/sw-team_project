from flask import session, request, jsonify, redirect, Blueprint, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_


# for checklist
from models import Routine, ChecklistDefault, ChecklistRoutine
import datetime
from connect_db import db


bp = Blueprint('checklist', __name__, url_prefix='/check')


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


@bp.route('/checklist', methods=["GET", "POST"])
def checklist():

    # 임의로 설정한 user & animal, 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1

    # 유저아이디, 동물아이디, 날짜, 요일
    current_user = session['login']
    current_animal = session['curr_animal']
    

    if request.method=="GET":
        current_date = request.headers['currdate']
        current_weekday_num = request.headers['weekday']

        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date)).first()
        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, 
                                            Routine.weekday == current_weekday_num)).all()

        # routine이 없음
        if routines == []:
            # checklist_default 기록이 있음 --> 수정으로 넘어감
            if checklist_default != None:
                return redirect(url_for('checklist.checklist_update'))

            # checklist_default 기록이 없음 --> 입력 폼만 반환
            else: 
                return "checklist_default form"


        # routine이 있음
        else: 
            # checklist_default 기록이 있음 --> 수정으로 넘어감
            if checklist_default != None:
                return redirect(url_for('checklist.checklist_update'))

            # checklist_default, checklist_routine 기록이 없음 --> routine json, 입력 폼 반환
            else:
                today_routines = query_to_dict(routines)
                return jsonify(today_routines)
   

    else: # POST

        currdate = request.headers['currdate']
        current_weekday_num = request.headers['weekday']

        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, 
                                            Routine.weekday == current_weekday_num)).all()

        checks = request.get_json() 

        # routine이 없음 --> checklist_default 생성
        if routines == []:
            animal_id = current_animal
            food = checks['food']
            bowels = checks['bowels']
            note = checks['note']

            new_cd = ChecklistDefault(currdate, animal_id, food, bowels, note)
            db.session.add(new_cd)

        # routine이 있음 --> checklist_default, checklist_routine 생성
        else:
            json_routines = checks['routines']
            animal_id = current_animal
            food = checks['food']
            bowels = checks['bowels']
            note = checks['note']

            new_cd = ChecklistDefault(currdate, animal_id, food, bowels, note)
            db.session.add(new_cd)

            j = 0
            for r in routines:
                j += 1

            for i in range(j):
                routine = json_routines[f'routine{i+1}']
                animal_id, routine_id, routine_name, status = current_animal, routine['routine_id'], routine['routine_name'], routine['status']
                new_cr = ChecklistRoutine(currdate, animal_id, routine_id, routine_name, status)
                db.session.add(new_cr)      
        
        db.session.commit()

    return jsonify(checks)


@bp.route('/update', methods=["GET", "POST"])
def checklist_update():

    # 임의로 설정한 user & animal, 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1

    # user, animal
    current_user = session['login']
    current_animal = session['curr_animal']


    if request.method=="GET": # GET
        current_date = request.headers['currdate']
        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date)).first()
        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == current_animal, 
                                                                ChecklistRoutine.currdate == current_date)).all()
        
        # checklist_default만 있음
        if checklists_routine == []:
            checklist_d = query_to_dict(checklist_default)
            return jsonify(checklist_d)

        # 둘 다 있음
        else: 
            checklist_d = query_to_dict(checklist_default)
            checklist_r = query_to_dict(checklists_routine)
            return jsonify(checklist_d, checklist_r)

    else: # POST

        current_date = request.headers['currdate']
        checks = request.get_json() 
        checklist_default = ChecklistDefault.query.filter(and_(ChecklistDefault.animal_id == current_animal, 
                                                                ChecklistDefault.currdate == current_date)).first()
        checklists_routine = ChecklistRoutine.query.filter(and_(ChecklistRoutine.animal_id == current_animal, 
                                                                ChecklistRoutine.currdate == current_date)).all()                                                        
        
        animal_id = session['curr_animal']

        # checklist_default만 수정
        if checklists_routine == []:
            food = checks['food']
            bowels = checks['bowels']
            note = checks['note']

            checklist_default.food = food
            checklist_default.bowels = bowels
            checklist_default.note = note

            db.session.commit()      
        
        # 둘 다 수정
        else:
            food, bowels, note = checks['food'], checks['bowels'], checks['note']

            checklist_default.food = food
            checklist_default.bowels = bowels
            checklist_default.note = note
            db.session.commit()  

            json_routines = checks['routines']

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
