from flask import Flask, render_template, jsonify, request, session, Blueprint
import boto3
import datetime
from connect_db import db
from sqlalchemy import and_
from models import Journal
import json

from werkzeug.utils import secure_filename
# from predict import padding, mk_img, predict_result

from config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION

import os

# app = Flask(__name__)
bp = Blueprint('journal', __name__, url_prefix='/')


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


# 파일 업로드 받아서 s3 업로드, 이미지 링크 반환
# def put_s3_img_url():
#     f = request.files['file']
#     newname = (str(datetime.datetime.now()).replace(":","")).replace(" ","_") + ".png"

#     imgpath = f"./static/{newname}"
#     f.save(imgpath)

#     s3.upload_file(imgpath, AWS_S3_BUCKET_NAME, newname)
#     img_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{newname}"
    
#     return img_url


s3 = s3_connection()


@bp.route('/journal', methods = ['GET', 'POST'])
def journal():
    # 임의로 설정한 user & animal, 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']
    current_date = datetime.datetime.now().date()

    ## ----------------------------------------------------------

    if request.method == 'GET':

        today_entry = Journal.query.filter(and_(Journal.user_id==current_user,
                                                Journal.currdate == current_date)).first()
        
        # 오늘의 기록 존재시
        if today_entry != None:
            today_entry = today_entry.__dict__
            del today_entry['_sa_instance_state']

            return jsonify(today_entry)

        # 오늘의 기록이 없을 시
        else:
            return "journal entry form"

    else: # POST

        journal_entry = request.form
        
        animal_id = current_animal
        user_id = current_user

        journal_entry = json.loads(journal_entry['data'])

        title = journal_entry['title']
        content = journal_entry['content']
        currdate = current_date


        try:
            f = request.files['file']
            newname = (str(datetime.datetime.now()).replace(":","")).replace(" ","_") + ".png"

            imgpath = f"./static/{secure_filename(newname)}"
            f.save(imgpath)

            s3.upload_file(imgpath, AWS_S3_BUCKET_NAME, newname)
            img_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{newname}"

            image = img_url

        except: 
            image = ""

        # 사진 업로드 시 사진 링크 반환, 일상 기록 db 저장 / 사진 업로드 x시 image 링크 ""
        new_entry = Journal(animal_id, user_id, title, image, content, currdate)
        db.session.add(new_entry)

        db.session.commit()
    
        return jsonify(new_entry)


# if __name__ == '__main__':
#     app.run(debug=True)

