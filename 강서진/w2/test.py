from flask import Flask, request, jsonify, session, Blueprint, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import Routine, ChecklistRoutine, ChecklistDefault, User
from connect_db import db
import json
from flask import flash
import datetime
from sqlalchemy import and_
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash





bp = Blueprint('main', __name__, url_prefix='/')
# current_time = datetime.datetime.now()
# weekday = current_time.weekday()

def to_weekday(num):
    weekdays = ['mon','tue','wed','thu','fri','sat','sun']
    num = int(num)
    return weekdays[num]

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


#------------------------------------------------------------------------------------------------------
@bp.route('/register', methods=['GET','POST']) #GET(????????????), POST(????????????) ????????? ??????
def register():
    
    if request.method=="POST":
        forms = request.get_json()
        userid = forms['userid']
        email = forms['email']
        password = forms['password']

        user = User(user_id = userid,
                        pw=generate_password_hash(password), email=email
                        )
        #????????? ??????
        check_email = User.query.filter(User.email==email).first()
        check_userid = User.query.filter(User.userid==userid).first()
        
        if check_userid:
            flash("?????? ?????? ??????????????????.", category='error')
            return redirect(url_for('register'))
        if check_email:
            flash("?????? ????????? ??????????????????.", category='error')
            return redirect(url_for('register'))

         

        db.session.add(user)  # id, name ????????? ?????? ???????????? DB??? ??????
        db.session.commit()  #??????
        flash("????????????")
        return redirect(url_for('login'))

    

@bp.route('/login', methods=['GET','POST'])  
def login():
    if request.method=="POST":
        forms = request.get_json()
        userid = forms['userid']
        email = forms['email']
        password = forms['password'] 
         #????????? ??? ??????
         #????????? ??????
         
        
        user = User.query.filter(User.user_id == userid).first()
        if not user:
            error = "???????????? ?????? ??????????????????."
        elif not check_password_hash(userid, password):
            error = "??????????????? ???????????? ????????????."
        if error is None:
            session.clear()
            session['userid'] = userid #form?????? ????????? userid??? session??? ??????
            
            return jsonify(forms)
            
        flash(error)
        
        # return redirect('/') #???????????? ???????????? ??????????????? redirect
            
    return jsonify(forms) #?????? ????????? animal?????????..?

@bp.route('/logout',methods=['GET'])
def logout():
    session.pop('userid',None)
    return redirect(url_for('main'))

@bp.route('/')
def main():
    if 'userid' in session:  # session?????? userid??? ????????? ?????????
        return '????????? ??????! ???????????? %s' % escape(session['userid']) + \
            "<br><a href = '/logout'>????????????</a>"

    return "????????? ????????????. <br><a href = '/login'> ????????? ????????????! </a>" # ???????????? ?????? ??????

#-------------------------------------------------------------------------------------------------------
# @bp.route('/animal', methods=['Post'])
# def animal():
#     param = request.get_json() 
#     session['animal_id'] = param['animal_id'] 
    
#     return jsonify(param) 

#??? ?????? ??????
@bp.route('/routine', methods=['POST']) 
def routine():
    param = request.get_json() #json: animal_id, routine_name, date:{mon=true,tue=true...}, 
    
    #json?????? ??? ??? ?????? ????????? ??????
     
    routine_name = param['routine_name']
    animal_id = param['animal_id']

     
    date_dict = param['weekday'] #date ????????? json array??? object??? ??????
    routine_date = [] #?????????
    for key, val in date_dict.items():
        if val=='true':
            routine_date.append(key) #true??? ???????????? ??????


    #????????? routine ?????? ?????????
    for i in range(len(routine_date)): #???, ???, ??? 3??? ??????
        routine = Routine(animal_id=animal_id, routine_name=routine_name, weekday=routine_date[i]) 
        #db??? ??????, ????????????
        db.session.add(routine)
        db.session.commit()

    #json ??????
    return jsonify(param)



#?????? ????????? ?????????????????? ?????? ?????? ?????? 
@bp.route('/weekdaydelete', methods=['POST']) 
def weekdaydelete():
    param = request.get_json() #json: routine_name, animal_id, del_date
    
    #json?????? ??? ??? ?????? ????????? ??????
     
    routine_name = param['routine_name']
    animal_id = param['animal_id'] 
    del_date = param['weekday'] #date ????????? json array??? object??? ??????

    


    #?????? db ??????
    # for i in range(len(not_routine_date)): #?????????
    del_routine = Routine.query.filter(and_(Routine.animal_id == animal_id, Routine.routine_name==routine_name,
                                                                Routine.weekday == del_date)).first() #??????????????? ??????????????? row ??????
        
    del_routine.routine_id
    del_r = Routine.query.get(del_routine.routine_id)
    db.session.delete(del_r)
    db.session.commit()

    #json ??????
    return jsonify(param)


#?????? ??????: ?????? ???????????? ????????? ????????? ?????? ?????? ????????? ???????????? 
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

        

#---------------------------------------------------------------------------------------------------------------------
# -----------------
# from number to weekday
# -----------------


@bp.route('/checklist', methods=["GET", "POST"])
def checklist():

    # ????????? ????????? user & animal, ????????? ??????
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


        # routine??? ?????? --> default??? 
        if routines == []:
            # checklist_default ????????? ?????? --> ???????????? ?????????
            if checklist_default != None:
                return redirect(url_for('checklist_update'))

            # checklist_default ????????? ?????? --> ?????? ?????? ??????
            else: 
                return "checklist_default form"


        # routine??? ?????? --> default??? routine ??? ???
        else: 
            # checklist_default ????????? ?????? 
            # (== ???????????? checklist_routine ????????? ??????) --> ???????????? ?????????
            if checklist_default != None:
                # today_routines = query_to_dict(routines)
                # checklist_d = query_to_dict(checklist_default)
                # checklist_r = query_to_dict(checklists_routine)
                return redirect(url_for('checklist_update'))

            # checklist_default, checklist_routine ????????? ?????? --> routine json, ?????? ??? ??????
            else:
                today_routines = query_to_dict(routines)
                return jsonify(today_routines)
   

    else: # POST

        routines = Routine.query.filter(and_(Routine.animal_id == current_animal, Routine.weekday == current_weekday_num)).all()
        checks = request.get_json() 

        # ????????? routine??? ?????? --> checklist_default??? ??????
        if routines == []:
            new_cd = json_to_new_cd(checks)
            db.session.add(new_cd)

        # ????????? routine??? ?????? --> checklist_default??? checklist_routine ??????
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


@bp.route('/update', methods=["GET", "POST"])
def checklist_update():

    # ????????? ????????? user & animal, ????????? ??????
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
        

        # routine??? ?????? 
        if routines == []:
            # checklist_default??? ?????? ???????????? redirect???
            checklist_d = query_to_dict(checklist_default)
            
            return jsonify(checklist_d)


        # routine??? ??????
        else: 
            # checklist_default, checklist_routine??? ?????? ?????? ????????? redirect???
            # # routines, checklist_default??? checklist_routine ??????
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

        # checklist_default??? ?????? ???
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
#     app.run()