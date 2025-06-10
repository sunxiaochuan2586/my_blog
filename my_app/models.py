# my_app/models.py
from my_app import db, login_manager # 从 __init__.py 导入
from flask_login import UserMixin
from datetime import datetime,timezone


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    # ... User 类的所有代码，原封不动地从 app.py 复制过来 ...
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Post(db.Model):
    # ... Post 类的所有代码，原封不动地从 app.py 复制过来 ...
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"   