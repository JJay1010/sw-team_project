from flask import Flask, request, jsonify, session, Blueprint
from flask_sqlalchemy import SQLAlchemy
from pybo.model import Routine
from pybo.connect_db import db
import json
bp = Blueprint('main', __name__, url_prefix='/')

# @bp.route('/animal', methods=['Post'])
# def animal():
#     param = request.get_json() 
#     session['animal_id'] = param['animal_id'] 
    
#     return jsonify(param) 

#post
@bp.route('/routine', methods=['POST']) 
def routine():
    param = request.get_json() #json받기
    
    #json에서 각 값 임의 변수에 저장
     
    routine_name = param['routine_name']
    animal_id = param['animal_id']

     
    date_dict = param['date'] #date 부분의 json array를 object로 변환
    routine_date = []
    for key, val in date_dict.items():
        if val=='true':
            routine_date.append(key) #true인 요일값들 저장


    #모델로 routine 객체 만들기
    for i in range(len(routine_date)):
        routine = Routine(animal_id=animal_id, routine_name=routine_name, date=routine_date[i]) 
        #db에 저장, 업데이트
        db.session.add(routine)
        db.session.commit()

    #json 반환
    return jsonify(param)


# if __name__ == "__main__":
#     app.run()
