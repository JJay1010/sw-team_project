from flask import Flask, render_template, request, Blueprint
from werkzeug.utils import secure_filename
import boto3
import datetime
import os
# from predict import padding, mk_img, predict_result

from config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION

import os

app = Flask(__name__)


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


def get_s3_img_url(f):
    newname = (str(datetime.datetime.now()).replace(":","")).replace(" ","_") + ".png"

    imgpath = f"./static/{newname}"
    f.save(imgpath)

    s3.upload_file(imgpath, AWS_S3_BUCKET_NAME, newname)
    img_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{newname}"
    
    return img_url


s3 = s3_connection()


@app.route('/', methods = ['GET', 'POST'])
def file_upload():
    if request.method == 'GET':



        return render_template('index.html')
        


    else: # GET
        f = request.files['file']

        # 사진 업로드 시 사진 링크 반환, 일상 기록 db 저장
        if f:
            img_url = get_s3_img_url(f)

            return render_template('index.html', img_url=img_url)
        
        # 사진 업로드 x시 기록만 db 저장
        else:
            return 


if __name__ == '__main__':
    app.run(debug=True)


