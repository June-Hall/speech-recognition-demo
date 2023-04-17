import os
import re
import deepspeech
import wave
from pydub import AudioSegment
import numpy as np

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user


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
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/uploads', methods=['POST'])
def uploads():
    try:
        file = request.files['file']
        if file.filename == "":
            raise Exception
    except Exception:
        exit()
    print('hr3')
    file.save(os.path.join(
        app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
    text = infer(file.filename)

    return text


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


@app.route('/signout')
@login_required
def signout():
    logout_user()
    flash('再见!')
    return redirect(url_for('index'))


@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于 return {'user': user}


@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html'), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


def infer(file):
    # 定义语音文件路径
    # mp3 转换 wav
    audio_path = os.path.join('audio', file)
    try:
        print(audio_path.endswith(".mp3"))
        if (audio_path.endswith(".mp3")):
            pattern = re.compile(r'(.*)\.mp3')
            match = pattern.match(file)
            if match:
                filename = match.group(1)
            wav_audio = AudioSegment.from_file(audio_path, format='mp3').set_frame_rate(
                16000).set_channels(1).set_sample_width(2)
            wav_audio.export(os.path.join(
                'audio', filename + ".wav"), format='wav')
            audio_path = os.path.join('audio', filename + ".wav")
            print('*'*100, audio_path)
        elif (audio_path.endswith(".ogg")):
            pattern = re.compile(r'(.*)\.ogg')
            match = pattern.match(file)
            if match:
                filename = match.group(1)
            wav_audio = AudioSegment.from_file(audio_path, format='ogg').set_frame_rate(
                16000).set_channels(1).set_sample_width(2)
            wav_audio.export(os.path.join(
                'audio', filename + ".wav"), format='wav')
            audio_path = os.path.join('audio', filename + ".wav")
            print('*'*100, audio_path)
        elif (audio_path.endswith(".raw")):
            pattern = re.compile(r'(.*)\.raw')
            match = pattern.match(file)
            if match:
                filename = match.group(1)
            wav_audio = AudioSegment.from_file(
                audio_path, format='raw').set_frame_rate(16000).set_channels(1).set_sample_width(2)
            wav_audio.export(os.path.join(
                'audio', filename + ".wav"), format='wav')

            audio_path = os.path.join('audio', filename + ".wav")
            print('*'*100, audio_path)
        else:
            raise Exception
    except Exception:
        Exception.with_traceback()
        exit()

    # 加载 DeepSpeech 模型
    model_path = 'DeepSpeech/deepspeech-0.9.3-models.pbmm'
    beam_width = 500
    model = deepspeech.Model(model_path)
    model.beamWidth = beam_width

    # 加载语音文件
    with wave.open(audio_path, 'rb') as audio_file:
        audio_data = np.frombuffer(audio_file.readframes(
            audio_file.getnframes()), np.int16)

    # 将语音转换成文本
    text = model.stt(audio_data)
    print("识别结果：", text)
    return text


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))


# run
if __name__ == '__main__':
    app.run()
