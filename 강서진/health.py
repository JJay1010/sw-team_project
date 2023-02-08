from flask import url_for, redirect, jsonify, request, session, Blueprint
import boto3
import datetime
from connect_db import db
from sqlalchemy import and_
from models import Health
import json

from werkzeug.utils import secure_filename
# from predict import padding, mk_img, predict_result

from config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION

import os

bp = Blueprint('health', __name__, url_prefix='/')

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
    except TypeError:
        return None


s3 = s3_connection()

@bp.route('/health_records', methods=["GET"])
def health_records():
    # 임의로 설정한 user & animal, 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']
    current_date = datetime.datetime.now().date()


    health_records = Health.query.filter(and_(Health.user_id==current_user,
                                            Health.animal_id==current_animal)).all()

    health_records = query_to_dict(health_records)
    # print(health_records)
    return jsonify(health_records)