from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import datetime
import boto3
# from predict import padding, mk_img, predict_result

from config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION


app = Flask(__name__)


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

@app.route('/index', methods = ['GET', 'POST'])
def file_upload():
    if request.method == 'POST':

        f = request.files['file']
        print(request.values)
        # f.save(secure_filename(f.filename))

        newname = (str(datetime.datetime.now()).replace(":","")).replace(" ","_") + ".png"

        imgpath = f"./static/{secure_filename(newname)}"
        f.save(imgpath)

        s3.upload_file(imgpath, AWS_S3_BUCKET_NAME, newname)
        img_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/{newname}"

        return render_template('index.html', img_url=img_url)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)