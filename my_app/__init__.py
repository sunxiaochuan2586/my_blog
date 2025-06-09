# my_app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import timezone
from zoneinfo import ZoneInfo
from markdown import markdown
from typing import Optional, Any

# 先创建扩展的实例，但不传入 app
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "routes.login"
login_manager.login_message_category = "info"  # type: ignore
login_manager.login_message = "请先登录以访问此页面。"


def create_app(config_class: Any = "my_app.config.Config") -> Flask:
    # `instance_relative_config=True` 允许从 instance 文件夹加载配置
    app = Flask(__name__, instance_relative_config=True)
    
    # 从配置对象加载配置
    app.config.from_object(config_class)

    # 将扩展实例与 app 实例进行绑定
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # 在函数内部导入并注册蓝图，避免循环依赖
    from my_app.routes import routes_bp
    app.register_blueprint(routes_bp)

    from my_app.commands import commands_bp
    app.register_blueprint(commands_bp)

    # --- 自定义模板过滤器 ---
    @app.template_filter("to_local_time")
    def to_local_time(utc_dt: Optional[Any], fmt: str = "%Y-%m-%d %H:%M") -> str:
        if utc_dt is None:
            return ""
        # 修正时区为上海（北京时间），以匹配前端模板文本
        local_tz = ZoneInfo("Asia/Shanghai")
        local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(local_tz)
        return local_dt.strftime(fmt)

    @app.template_filter("md")
    def markdown_to_html(txt: str) -> str:
        # 将 Markdown 文本转换为 HTML，启用代码高亮和表格扩展
        return markdown(txt, extensions=["fenced_code", "tables"])

    return app
