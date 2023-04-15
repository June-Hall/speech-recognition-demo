import os

from models import SigninForm
from models import db, User

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + \
    os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

db.create_all()


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/Users/duke/Desktop/learn/code/python/python选修/final/speech-recognition-demo/audio/'
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        # 处理表单数据
        username = form.username.data
        password = form.password.data
        print(username, password)
        # 存储用户信息到数据库
        # ...
        return redirect(url_for('index'))
    return render_template('signin.html', form=form)


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

        flash('文件上传成功！')
        return render_template('index.html')
    else:

        return render_template('index.html')


if __name__ == '__main__':
    app.run()
