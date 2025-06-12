# my_app/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Length, Email, Optional, ValidationError
from ..models import User
from wtforms.validators import Length, URL # 导入 URL 验证器

class AdminEditUserForm(FlaskForm):

    username = StringField('用户名', validators=[Length(min=2, max=20)])
    email = StringField('邮箱', validators=[Email()])
    bio = TextAreaField('个性签名', validators=[Optional(), Length(max=200)])
    password = PasswordField('新密码 (如不修改请留空)', validators=[Optional(), Length(min=6)])
    is_admin = BooleanField('设为管理员')
    github_url = StringField('GitHub URL', validators=[Length(max=255), URL()]) # 添加这一行
    website_url = StringField('个人网站', validators=[Length(max=255), URL()]) # 添加这一行
    submit = SubmitField('保存更改')

    def __init__(self, original_user, *args, **kwargs):
        super(AdminEditUserForm, self).__init__(*args, **kwargs)
        self.original_user = original_user

    def validate_username(self, username):
        if username.data != self.original_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('该用户名已被使用，请选择其他用户名。')

    def validate_email(self, email):
        if email.data != self.original_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('该邮箱已被注册，请选择其他邮箱。')
