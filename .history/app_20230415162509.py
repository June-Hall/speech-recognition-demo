from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/Users/duke/Desktop/learn/code/python/python选修/final/speech-recognition-demo/audio/'
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signin')
def signin():

    return render_template('signin.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        f = request.files['file']
        print(request.files)
        f.save(os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))

        # return '文件上传成功！'
        return render_template('index.html')
    else:

        return render_template('index.html')


if __name__ == '__main__':
    app.run()
