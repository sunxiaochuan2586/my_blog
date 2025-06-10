# my_app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import timezone
from zoneinfo import ZoneInfo
from typing import Optional, Any
import mistune      # 1. 导入 mistune
import markupsafe   # 2. 导入 markupsafe

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = "routes.login"
login_manager.login_message_category = "info"
login_manager.login_message = "请先登录以访问此页面。"

# ▼▼▼ 3. 添加自定义的高亮渲染器 (这是让高亮生效的关键) ▼▼▼
class HighlightRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info=None):
        if info:
            lang = markupsafe.escape(info.strip().split(None, 1)[0])
            # 生成 highlight.js 需要的 class="language-xxx"
            return f'<pre><code class="language-{lang}">{markupsafe.escape(code)}</code></pre>\n'
        # 如果没有指定语言，也生成正确的标签结构
        return f'<pre><code>{markupsafe.escape(code)}</code></pre>\n'

# 4. 创建一个使用我们自定义渲染器的 Markdown 实例
markdown_renderer = mistune.create_markdown(renderer=HighlightRenderer())

# 5. 定义新的过滤器函数，它将使用上面的渲染器
def markdown_filter(text: str) -> str:
    return markupsafe.Markup(markdown_renderer(text))

def create_app(config_class: Any = "my_app.config.Config") -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from my_app.routes import routes_bp
    app.register_blueprint(routes_bp)
    from my_app.commands import commands_bp
    app.register_blueprint(commands_bp)
    from my_app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    @app.template_filter("to_local_time")
    def to_local_time(utc_dt: Optional[Any], fmt: str = "%Y-%m-%d %H:%M") -> str:
        if utc_dt is None: return ""
        local_tz = ZoneInfo("Asia/Shanghai")
        local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(local_tz)
        return local_dt.strftime(fmt)

    # ▼▼▼ 6. 注册我们全新的 'md' 过滤器，替换掉旧的那个 ▼▼▼
    app.jinja_env.filters['md'] = markdown_filter

    return app