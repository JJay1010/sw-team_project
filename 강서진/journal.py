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


@bp.route('/journals/<current_user>', methods = ['GET'])
def journals(current_user):
    # 임의로 설정한 user & animal, 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']
    current_date = datetime.datetime.now().date()

    ## ----------------------------------------------------------

    if request.method == 'GET':
        
        # 최신순으로
        journals = Journal.query.filter(and_(Journal.user_id==current_user,
                                            Journal.animal_id==current_animal)).all()
        
        # 기록 존재시
        if journals != None:
            journals = query_to_dict(journals)
            return jsonify(journals)

        # 기록이 없을 시
        else:
            return None


# 아이템 클릭 시 기록 열람
@bp.route('/content/<int:journal_index>', methods=["GET"])
def journal_content(journal_index):

    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']

    journal_entry = Journal.query.get(journal_index)
    
    journal_entry = journal_entry.__dict__
    del journal_entry['_sa_instance_state']
    return jsonify(journal_entry)

    
@bp.route('/factory', methods=["GET","POST"])
def journal_factory():
    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']
    current_date = datetime.datetime.now().date()

    if request.method == "GET":
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
    
        return "journal successfully created"


@bp.route('/update/<int:journal_index>', methods=["GET","POST"])
def journal_update(journal_index):

    # 나중에 삭제
    session['login'] = 'test'
    session['curr_animal'] = 1

    current_user = session['login']
    current_animal = session['curr_animal']
    current_date = datetime.datetime.now().date()

    editing_entry = Journal.query.get(journal_index)

    existing_entry = editing_entry.__dict__
    del existing_entry['_sa_instance_state']

    if request.method == 'GET':
        return jsonify(existing_entry)

    else: # POST

        changes = request.form
        changes = json.loads(changes['data'])

        title = changes['title']
        content = changes['content']

        f = request.files['file']

        # 새로 이미지 업로드
        if f:
            # 기존의 이미지 삭제
            try:
                s3.delete_object(
                    Bucket = AWS_S3_BUCKET_NAME,
                    Key = (editing_entry.image).split('/')[-1]
                )

            # 기존에 이미지가 없었던 경우
            except: 
                pass

            newname = (str(datetime.datetime.now()).replace(":","")).replace(" ","_") + ".png"

            imgpath = f"./static/{secure_filename(newname)}"
            f.save(imgpath)
            
            s3.upload_file(imgpath, AWS_S3_BUCKET_NAME, newname)
            img_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{newname}"

            editing_entry.title = title
            print(editing_entry.title)
            editing_entry.content = content
            editing_entry.image = img_url


        # 새로 이미지 업로드 X --> 기존의 image 칼럼 데이터 그대로 유지
        else:
            editing_entry.title = title
            editing_entry.content = content

        # 이미지 삭제 시에는???

        db.session.commit()
    return "successfully updated"


@bp.route('/delete/<int:journal_index>',methods=["DELETE"])
def journal_delete(journal_index):

    deleting_journal = Journal.query.get(journal_index)

    s3.delete_object(
                Bucket = AWS_S3_BUCKET_NAME,
                Key = (deleting_journal.image).split('/')[-1]
            )

    db.session.delete(deleting_journal)
    db.session.commit()
    
    return "successfully removed"
