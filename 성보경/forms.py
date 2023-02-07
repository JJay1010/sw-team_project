
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from models import User

class RegisterForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired('아이디는 필수 항목입니다.'), Length(min = 4, max = 20)])
    email = EmailField('email', validators=[DataRequired('이메일은 필수 항목입니다.'), Email('유효하지 않은 이메일입니다.')] )
    password = PasswordField('password', validators=[DataRequired('비밀번호를 입력해주세요.'), EqualTo('re_password', '비밀번호가 일치하지 않습니다.')])
    re_password = PasswordField('re_password', validators=[DataRequired('비밀번호를 한 번 더 입력해주세요.')])

    
class LoginForm(FlaskForm):
    class UserPassword(object):
        def __init__(self, message=None):
            self.message = message
        def __call__(self,forms,field):
            userid = forms['userid'].data
            password = field.data

            user = User.query.filter_by(userid=userid).first()

            if user.check_password(password) == False:
                raise ValueError('Wrong password')

    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), UserPassword()]) 