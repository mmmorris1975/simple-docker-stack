import os
import boto3

from botocore.exceptions import ClientError
from flask import Flask, request, render_template, flash, redirect, url_for, abort
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from wtforms import Form, FileField

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_FOLDER'] = '/var/tmp/uploads'
app.config['SECRET_KEY'] = 'qrDOSHOofq8a0485;;asuqrq'

s3 = boto3.client('s3')


class UploadForm(Form):
    file = FileField(label='File')


@app.route('/', methods=['GET', 'POST'])
def index():
    f = UploadForm(request.form)
    if request.method == 'POST' and f.validate():
        if 'file' in request.files:
            file = request.files['file']

            if file.filename.strip() == '':
                flash('No selected file')
                return redirect(request.url)

            try:
                s3.put_object(Bucket=os.getenv('S3_BUCKET_NAME'), Key=secure_filename(file.filename),
                              Body=file.stream, ACL='private')
            except ClientError as e:
                app.logger.error("S3 put_object(): %s", e)
                abort(401)
        else:
            flash('No file part')
            return redirect(request.url)

    return render_template('form.html', form=f)


@app.errorhandler(RequestEntityTooLarge)
def large_upload(e):
    app.logger.error("Upload request too large - MAX: %d bytes", app.config['MAX_CONTENT_LENGTH'])
    flash("Max upload size is %0.2f MB" % (app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)))
    return redirect(url_for('index'))

with open('/dev/urandom', 'r+b') as d:
    b = d.read(400*1024*1024)
