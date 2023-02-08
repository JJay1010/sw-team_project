from flask import url_for, redirect, jsonify, request, session, Blueprint
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
                                                Journal.animal_id==current_animal,
                                                Journal.currdate == current_date)).first()
        
        # 오늘의 기록 존재시
        if today_entry != None:

            return redirect(url_for('journal.journal_update'))

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
    
        return "success"


@bp.route('/journal_update', methods=["GET","POST"])
def journal_update():
    # 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']
    current_date = datetime.datetime.now().date()

    if request.method == 'GET':

        today_entry = Journal.query.filter(and_(Journal.user_id==current_user,
                                                Journal.animal_id==current_animal,
                                                Journal.currdate == current_date)).first()

        today_entry = today_entry.__dict__
        del today_entry['_sa_instance_state']
        return jsonify(today_entry)

    else: #POST

        today_entry = Journal.query.filter(and_(Journal.user_id==current_user,
                                                Journal.animal_id==current_animal,
                                                Journal.currdate == current_date)).first()

        journal_entry = request.form
        journal_entry = json.loads(journal_entry['data'])

        title = journal_entry['title']
        content = journal_entry['content']
        currdate = current_date

        f = request.files['file']
        # 새로 이미지 업로드 시
        if f:
            # 기존의 이미지 삭제
            s3.delete_object(
                Bucket = AWS_S3_BUCKET_NAME,
                Key = (today_entry.image).split('/')[-1]
            )

            newname = (str(datetime.datetime.now()).replace(":","")).replace(" ","_") + ".png"

            imgpath = f"./static/{secure_filename(newname)}"
            f.save(imgpath)

            s3.upload_file(imgpath, AWS_S3_BUCKET_NAME, newname)
            img_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{newname}"

            today_entry.title = title
            today_entry.content = content
            today_entry.image = img_url

        # 새로 이미지 업로드 X --> 기존의 image 칼럼 데이터 그대로 유지
        else:

            today_entry.title = title
            today_entry.content = content

        db.session.commit()
    return "update successful"


# if __name__ == '__main__':
#     app.run(debug=True)
