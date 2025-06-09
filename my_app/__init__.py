# my_app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate  # 1. 导入 Migrate 类
from datetime import timezone
from zoneinfo import ZoneInfo
from markdown import markdown
from typing import Optional, Any

# 先创建扩展的实例
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()  # 2. 创建 Migrate 的实例

# LoginManager 的配置
login_manager.login_view = "routes.login"
login_manager.login_message_category = "info"
login_manager.login_message = "请先登录以访问此页面。"


def create_app(config_class: Any = "my_app.config.Config") -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_object(config_class)

    # 将扩展实例与 app 实例进行绑定
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # 3. 初始化 migrate，并告诉它要关联哪个 app 和哪个 db

    # 在函数内部导入并注册蓝图
    from my_app.routes import routes_bp
    app.register_blueprint(routes_bp)

    from my_app.commands import commands_bp
    app.register_blueprint(commands_bp)

    # 确保后台管理的蓝图也被注册了
    from my_app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    # --- 自定义模板过滤器 ---
    @app.template_filter("to_local_time")
    def to_local_time(utc_dt: Optional[Any], fmt: str = "%Y-%m-%d %H:%M") -> str:
        if utc_dt is None:
            return ""
        local_tz = ZoneInfo("Asia/Shanghai")
        local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(local_tz)
        return local_dt.strftime(fmt)

    @app.template_filter("md")
    def markdown_to_html(txt: str) -> str:
        return markdown(txt, extensions=["fenced_code", "tables"])

    return app