from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from my_app.models import User, Post
from functools import wraps  # <-- 1. 导入 wraps
# 创建一个名为 'admin' 的新蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 这是一个自定义的装饰器，用于检查管理员权限
def admin_required(f):
    @wraps(f)  # <-- 2. 在这里加上 @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# 所有的后台路由都应该以 admin_bp.route 开头
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """后台管理主页"""
    user_count = User.query.count()
    post_count = Post.query.count()

    # ▼▼▼ 插入终极诊断代码 ▼▼▼
    import os
    print("\n--- 文件系统最终诊断 ---")
    # 获取当前文件所在的目录，然后推算出项目根目录和模板目录
    # 这比依赖 "当前工作目录" 更可靠
    try:
        current_file_path = os.path.abspath(__file__)
        my_app_admin_dir = os.path.dirname(current_file_path)
        my_app_dir = os.path.dirname(my_app_admin_dir)
        
        # 我们要检查的两个关键路径
        templates_dir = os.path.join(my_app_dir, 'templates')
        admin_templates_dir = os.path.join(templates_dir, 'admin')
        target_file = os.path.join(admin_templates_dir, 'dashboard.html')

        print(f"1. 'templates' 文件夹路径: {templates_dir}")
        print(f"   是否存在? {os.path.exists(templates_dir)}")
        
        print(f"2. 'templates/admin' 文件夹路径: {admin_templates_dir}")
        print(f"   是否存在? {os.path.exists(admin_templates_dir)}")

        if os.path.exists(admin_templates_dir):
            print(f"   'templates/admin' 文件夹内容: {os.listdir(admin_templates_dir)}")

        print(f"3. 目标文件 'dashboard.html' 完整路径: {target_file}")
        print(f"   是否存在? {os.path.exists(target_file)}")

    except Exception as e:
        print(f"诊断代码自身发生错误: {e}")
    
    print("--- 诊断结束，准备渲染模板... ---\n")
    # ▲▲▲ 诊断代码结束 ▲▲▲

    return render_template(
        'admin/dashboard.html', 
        title='后台管理', 
        user_count=user_count, 
        post_count=post_count
    )


# 你可以继续添加其他管理页面，比如用户列表
@admin_bp.route('/users')
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/user_list.html', title='用户管理', users=users)

# my_app/admin/routes.py

@admin_bp.route('/posts')
@admin_required
def post_list():
    all_posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('admin/post_list.html', title='文章管理', posts=all_posts)