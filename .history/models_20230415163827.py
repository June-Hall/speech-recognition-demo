from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class SigninForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')
