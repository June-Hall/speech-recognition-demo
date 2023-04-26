import os
import re
import deepspeech
import wave
from pydub import AudioSegment
import numpy as np
import sounddevice as sd

from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user


from speech_recognition import app, db
from speech_recognition.models import SigninForm, SignupForm, User


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
    file.save(os.path.join(
        app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
    text = infer(file.filename)

    return text


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


@app.route('/record', methods=['POST'])
def record():
    # 初始化 DeepSpeech 模型
    model_path = 'speech_recognition/DeepSpeech/deepspeech-0.9.3-models.pbmm'  # 模型文件路径
    beam_width = 500
    model = deepspeech.Model(model_path)
    model.setBeamWidth(beam_width)

    # 录制音频并进行识别
    duration = 10  # 录制时长（秒）
    sample_rate = 16000  # 采样率
    channels = 1  # 音频通道数

    def audio_callback(indata, frames, time, status):
        audio_data.append(indata.copy())

    # 创建录音缓冲区
    audio_data = []

    # 录制音频
    with sd.InputStream(samplerate=sample_rate, channels=channels, callback=audio_callback):
        print("开始录音...")
        sd.sleep(duration * 1000)
        print("录音完成.")

    # 将录音数据转换为 numpy 数组
    audio_data = np.concatenate(audio_data)
    audio_data = np.ravel(audio_data)
    audio_data = (audio_data * 32767).astype(np.int16)

    # 语音识别
    text = model.stt(audio_data)
    print("识别结果：", text)
    return text


def infer(file):
    # 定义语音文件路径
    # mp3 转换 wav
    audio_path = os.path.join('speech_recognition/audio', file)
    try:
        if (audio_path.endswith(".mp3")):
            pattern = re.compile(r'(.*)\.mp3')
            match = pattern.match(file)
            if match:
                filename = match.group(1)
            wav_audio = AudioSegment.from_file(audio_path, format='mp3').set_frame_rate(
                16000).set_channels(1).set_sample_width(2)
            wav_audio.export(os.path.join(
                'speech_recognition/audio', filename + ".wav"), format='wav')
            audio_path = os.path.join('speech_recognition/audio', filename + ".wav")
            print('*'*100, audio_path)
        elif (audio_path.endswith(".ogg")):
            pattern = re.compile(r'(.*)\.ogg')
            match = pattern.match(file)
            if match:
                filename = match.group(1)
            wav_audio = AudioSegment.from_file(audio_path, format='ogg').set_frame_rate(
                16000).set_channels(1).set_sample_width(2)
            wav_audio.export(os.path.join(
                'speech_recognition/audio', filename + ".wav"), format='wav')
            audio_path = os.path.join('speech_recognition/audio', filename + ".wav")
            print('*'*100, audio_path)
        elif (audio_path.endswith(".raw")):
            pattern = re.compile(r'(.*)\.raw')
            match = pattern.match(file)
            if match:
                filename = match.group(1)
            wav_audio = AudioSegment.from_file(
                audio_path, format='raw').set_frame_rate(16000).set_channels(1).set_sample_width(2)
            wav_audio.export(os.path.join(
                'speech_recognition/audio', filename + ".wav"), format='wav')

            audio_path = os.path.join('speech_recognition/audio', filename + ".wav")
            print('*'*100, audio_path)
        elif (audio_path.endswith(".wav")):
            print('*'*100, audio_path)
        else:
            raise Exception
    except Exception:
        Exception.with_traceback()
        exit()

    # 加载 DeepSpeech 模型
    model_path = 'speech_recognition/DeepSpeech/deepspeech-0.9.3-models.pbmm'
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
