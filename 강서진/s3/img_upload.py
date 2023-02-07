from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import datetime
import os
# from predict import padding, mk_img, predict_result

from config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION
from connect_s3 import s3_connection, s3_put_object, s3_get_object

import os

app = Flask(__name__)


s3 = s3_connection()

@app.route('/', methods = ['GET', 'POST'])
def file_upload():
    if request.method == 'POST':

        f = request.files['file']
        newname = (str(datetime.datetime.now()).replace(":","")).replace(" ","_") + ".png"

        imgpath = f"./static/{newname}"
        f.save(imgpath)

        ret = s3_put_object(s3, AWS_S3_BUCKET_NAME, imgpath, newname)

        if ret:
            print("success")

            img_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{newname}"

            return render_template('index.html', img_url=img_url)

        else:
            print("failed")
        return render_template('index.html')

    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


