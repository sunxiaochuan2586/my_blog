# my_app/config.py
import os

# 定义项目的根目录
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    """设置 Flask 应用的配置变量。"""

    # 强烈建议将 SECRET_KEY 设置为环境变量，这里提供一个默认值作为备用
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_very_secret_and_unguessable_string_for_my_blog')

    # --- 数据库配置 ---
    # 将数据库文件存放在项目根目录下的 'instance' 文件夹中，这是一个推荐的做法
    # Flask 会自动创建这个文件夹
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'blog.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
