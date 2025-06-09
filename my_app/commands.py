# my_app/commands.py
import click
from flask import Blueprint
from my_app import db

commands_bp = Blueprint('commands', __name__, cli_group=None)

@commands_bp.cli.command('init-db')
def init_db_command():
    """清除现有数据并创建新表。"""
    db.create_all()
    click.echo('数据库已初始化。')
