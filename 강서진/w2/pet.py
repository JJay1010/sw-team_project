from flask import Flask, request, jsonify, session, Blueprint, url_for, redirect
from models import User, Animal
from connect_db import db
from sqlalchemy import and_
import boto3
from config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY


bp = Blueprint("pet", __name__, url_prefix="/pet")


# s3 클라이언트 생성
def s3_connection():
    try:
        s3 = boto3.client(
            service_name="s3",
            region_name=AWS_S3_BUCKET_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        return s3

    except Exception as e:
        print(e)
        print('ERROR_S3_CONNECTION_FAILED') 


def query_to_dict(objs):
    try:
        lst = []
        for obj in objs:
            obj = obj.__dict__
            del obj['_sa_instance_state']
            lst.append(obj)
        return lst
    except TypeError: # non-iterable
        objs = objs.__dict__
        del objs['_sa_instance_state']
        return objs


s3 = s3_connection()


@bp.route('/management', methods=['GET'])
def management():
    # 유저아이디
    session['login'] = request.headers['user_id']

    # 해당 아이디로 등록한 동물 전부
    animal_list = Animal.query.filter(Animal.user_id==session['login']).all()
    animal_list = query_to_dict(animal_list)

    # 등록한 동물이 없음
    if animal_list == []:
        return redirect(url_for("authentification.register_animal"))
    
    # 등록한 동물이 있음
    else:
        # 동물 리스트 반환 - 선택 시 header로 animal_id 보내기?
        return jsonify(animal_list)


@bp.route('/profile', methods=["GET"])
def profile():
    # 동물 정보 조회
    session['login'] = request.headers['user_id']
    session['curr_animal'] = request.headers['animal_id']

    animal = Animal.query.filter_by(animal_id = session['curr_animal']).first()

    animal = query_to_dict(animal)
    return jsonify(animal)  


@bp.route('/update', methods=["GET","PUT"])
def info_update():
    session['login'] = request.headers['user_id']
    session['curr_animal'] = request.headers['animal_id']

    # 동물 정보 수정 페이지 접근
    if request.method == "GET":
        animal = Animal.query.filter_by(animal_id = session['curr_animal']).first()

        animal = query_to_dict(animal)
        return jsonify(animal)  

    # 수정 정보 전달 시
    else: # PUT
        changes = request.get_json()
        animal = Animal.query.filter_by(animal_id = session['curr_animal']).first()

        animal.animal_name = changes['animal_name']
        animal.bday = changes['bday']
        animal.sex = changes['sex']
        animal.neutered = changes['neutered']
        animal.weight = changes['weight']

        db.session.commit()

        return "successfully updated"


@bp.route('/delete', methods=["DELETE"])
def pet_delete():
    session['login'] = request.headers['user_id']
    session['curr_animal'] = request.headers['animal_id']

    try:
        animal = Animal.query.filter_by(animal_id = session['curr_animal']).first()
        db.session.delete(animal)
        db.session.commit()
        return "successfully removed"

    except:
        return "removal failed"
