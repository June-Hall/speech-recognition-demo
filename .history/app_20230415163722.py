from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class SigninForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


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
