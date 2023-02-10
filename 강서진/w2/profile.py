from flask import Flask, request, jsonify, session, Blueprint, url_for, redirect
from models import User, Animal
from connect_db import db
from sqlalchemy import and_
from flask import flash
from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
from config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY


bp = Blueprint("profile", __name__, url_prefix="/pet")


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
        lst = []
        objs = objs.__dict__
        del objs['_sa_instance_state']
        lst.append(objs)
        return lst


s3 = s3_connection()


@bp.route('/info', methods=['GET'])
def info():
    # 임의로 설정한 user & animal, 나중에 삭제
    session['login'] = 'testtest'
    
    current_user = session['login']
    # current_animal = session['curr_animal']


    # 해당 아이디로 등록한 동물이 있는지 확인
    animal = Animal.query.filter(Animal.user_id==session['login']).all()

    if animal == []:
        return redirect(url_for("authentification.register_animal"))
    
    else:
        animal_list = query_to_dict(animal)
        if len(animal_list) == 1:
            return redirect(url_for(""))
        return jsonify(animal_list)


@bp.route('/ind', methods=["GET"])
def ind_info():

    request.headers['animal_id']
    return 



@bp.route('/info_update', methods=["GET","POST"])
def info_update():

    return 