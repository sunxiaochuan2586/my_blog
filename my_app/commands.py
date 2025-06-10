# my_app/commands.py
import click
from flask import Blueprint
from my_app import db
from .models import User

commands_bp = Blueprint('commands', __name__)

@commands_bp.cli.command("make-admin")
@click.argument("email")
def make_admin(email):
    """将指定邮箱的用户设置为管理员。"""
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"错误: 找不到邮箱为 {email} 的用户。")
        return
    
    user.is_admin = True
    db.session.commit()
    print(f"成功! 用户 {user.username} ({user.email}) 现在是管理员了。")