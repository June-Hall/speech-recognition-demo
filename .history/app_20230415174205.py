import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_login import login_user, LoginManager, UserMixin


# init
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/Users/duke/Desktop/learn/code/python/python选修/final/speech-recognition-demo/audio/'
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + \
    os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
# models


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class SigninForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


class SignupForm(FlaskForm):
    username = StringField(
        '用户名', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        '确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')


# routes
@app.route('/')
def index():
    return render_template('index.html')


@login_manager.user_loader
def get_user(ident):
    return User.query.get(int(ident))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        # 处理表单数据
        username = form.username.data
        password = form.password.data
        # 从数据库中查询用户信息
        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password, password):
            flash('用户名或密码错误')
            return redirect(url_for('signin'))
        # 用户名和密码正确，登录成功
        login_user(user)
        flash('登录成功')
        return redirect(url_for('index'))
    return render_template('signin.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # 处理表单数据
        username = form.username.data
        password = form.password.data
        # 查询用户名是否已被注册
        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash('用户名已被注册')
            return redirect(url_for('signup'))
        # 创建新用户
        user = User(username=username,
                    password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录')
        return redirect(url_for('signin'))
    return render_template('signup.html', form=form)


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


# run
if __name__ == '__main__':
    app.run()
