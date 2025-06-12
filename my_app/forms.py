# my_app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from my_app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, URL, Optional

class RegistrationForm(FlaskForm):
    username = StringField('用户名',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱',
                        validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    confirm_password = PasswordField('确认密码',
                                     validators=[DataRequired(), EqualTo('password', message='两次输入的密码必须一致')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请换一个。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请换一个。')


class LoginForm(FlaskForm):
    email = StringField('邮箱',
                        validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()])
    content = TextAreaField('内容', validators=[DataRequired()])
    submit = SubmitField('发布')
    
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('当前密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired()])
    new_password2 = PasswordField(
        '确认新密码', 
        validators=[DataRequired(), EqualTo('new_password', message='两次输入的新密码必须一致！')]
    )
    submit = SubmitField('确认修改')

class EditProfileForm(FlaskForm):
    bio = TextAreaField('个性签名', 
                        validators=[Optional(), Length(min=0, max=200)],
                        render_kw={"placeholder": "介绍一下自己..."})
    
    github_url = StringField('GitHub 主页', 
                             validators=[Optional(), Length(max=255)],
                             render_kw={"placeholder": "用户名"}) # 修改 placeholder 以匹配你的意图
    website_url = StringField('个人网站', 
                              validators=[Optional(), URL(message='请输入有效的URL')],
                              render_kw={"placeholder": "https://your-website.com"})
    
    submit = SubmitField('保存更改')    