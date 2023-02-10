from flask import url_for, redirect, jsonify, request, session, Blueprint
import boto3
import datetime
from connect_db import db
from sqlalchemy import and_
from models import Journal
import json
import os

from werkzeug.utils import secure_filename
# from predict import padding, mk_img, predict_result

from config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION

# app = Flask(__name__)
bp = Blueprint('journal', __name__, url_prefix='/journal')


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


# 기록 목록 출력
@bp.route('/journals', methods = ['GET'])
def journals():
    # 임의로 설정한 user & animal, 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']

    ## ----------------------------------------------------------

    if request.method == 'GET':
        
        # order by도 넣어야 할 듯(최신순?)
        journals = Journal.query.filter(and_(Journal.user_id==current_user,
                                            Journal.animal_id==current_animal)).all()
        
        # 기록 존재시
        if journals != []:
            journals = query_to_dict(journals)
            return jsonify(journals)

        # 기록이 없을 시
        else:
            return None


# 아이템 클릭 시 기록 열람
@bp.route('/content', methods=["GET"])
def journal_content():

    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']

    journal_index = request.headers['index']
    journal_entry = Journal.query.get(int(journal_index))
    
    journal_entry = journal_entry.__dict__
    del journal_entry['_sa_instance_state']

    return jsonify(journal_entry)


# 기록 생성
# 에러 발생 시 반환하는 값?
@bp.route('/factory', methods=["GET","POST"])
def journal_factory():
    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']

    if request.method == "GET":
        return "journal entry form"
    
    else: # POST

        journal_entry = request.form
        
        animal_id = current_animal
        user_id = current_user

        journal_entry = json.loads(journal_entry['data'])

        title = journal_entry['title']
        content = journal_entry['content']
        currdate = request.headers['currdate']

        f = request.files['file']
        
        # 사진 업로드 시 사진 링크 반환, 일상 기록 db 저장 / 사진 업로드 x시 image 링크 ""
        if f:
            newname = (str(datetime.datetime.now()).replace(":","")).replace(" ","_") + ".png"

            imgpath = f"./static/{secure_filename(newname)}"
            f.save(imgpath) # 로컬에 저장

            s3.upload_file(imgpath, AWS_S3_BUCKET_NAME, newname) # s3에 업로드
            img_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{newname}"
            os.remove(imgpath) # 로컬에 저장된 파일 삭제

            image = img_url

        else: 
            image = ""

        new_entry = Journal(animal_id, user_id, title, image, content, currdate)
        db.session.add(new_entry)

        db.session.commit()
    
        return "journal successfully created"


# 기록 수정
@bp.route('/update', methods=["GET","PUT"])
def journal_update():

    # 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']
    
    current_date = request.headers['currdate']
    journal_index = request.headers['index']
    
    if request.method == 'GET':
        editing_entry = Journal.query.get(journal_index)
        
        existing_entry = editing_entry.__dict__
        del existing_entry['_sa_instance_state']
        return jsonify(existing_entry)


    else: # POST
        
        journal_index = request.headers['index']
        editing_entry = Journal.query.get(journal_index)
        
        changes = request.form
        changes = json.loads(changes['data'])

        title = changes['title']
        content = changes['content']

        f = request.files['file']

        # 새로 이미지 업로드
        if f:
            # 기존의 이미지 s3에서 삭제
            try:
                s3.delete_object(
                    Bucket = AWS_S3_BUCKET_NAME,
                    Key = (editing_entry.image).split('/')[-1]
                )

            # 기존에 이미지가 없었던 경우 -- pass
            except: 
                pass

            newname = (str(datetime.datetime.now()).replace(":","")).replace(" ","_") + ".png"
            imgpath = f"./static/{secure_filename(newname)}"
            f.save(imgpath)
            
            s3.upload_file(imgpath, AWS_S3_BUCKET_NAME, newname)
            img_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{newname}"
            editing_entry.image = img_url

        # 새로 이미지 업로드 X --> 기존의 image 칼럼 데이터 그대로 유지
        else:
            
            # 이미지가 있었는데 삭제하는 건?????

            pass

        editing_entry.title = title
        editing_entry.content = content

        db.session.commit()
    return "successfully updated"


# 기록 삭제 (header로 인덱스 받기 --> journal json 받아서 )
@bp.route('/delete',methods=["DELETE"])
def journal_delete():
    # journal_index = int(request.headers['index'])
    # deleting_journal = Journal.query.get(journal_index)

    deletion = request.get_json()

    journal_index = deletion['index']
    journal_title = deletion['title']

    deleting_journal = Journal.query.filter(and_(Journal.index == journal_index,
                                                Journal.title == journal_title)).first()

    if deleting_journal.image != "":
        s3.delete_object(
                        Bucket = AWS_S3_BUCKET_NAME,
                        Key = (deleting_journal.image).split('/')[-1]
                        )
    else:
        pass

    db.session.delete(deleting_journal)
    db.session.commit()
    
    return "successfully removed"