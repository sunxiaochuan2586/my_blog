# my_app/admin/routes.py

# --- 导入必要的模块 ---
# 从 Flask 框架导入蓝图、模板渲染、错误处理、闪现消息、重定向、URL构造和请求对象
from flask import Blueprint, render_template, abort, flash, redirect, url_for, request
# 从 Flask-Login 导入当前用户对象和登录保护装饰器
from flask_login import current_user, login_required
# 从你的应用模型中导入用户和文章的数据库模型，以及数据库实例
from ..models import User, Post, db
# 导入你的 bcrypt 实例，用于密码哈希处理
from .. import bcrypt
# 导入管理员专用的编辑用户表单
from .forms import AdminEditUserForm
# 从 SQLAlchemy 导入 func，用于执行数据库函数（如 SUM）
from sqlalchemy import func
# 从 functools 导入 wraps，用于创建装饰器
from functools import wraps

# --- 1. 管理员权限装饰器 ---
# 定义一个装饰器，用于保护路由，确保只有管理员才能访问
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查当前用户是否已登录并且是管理员
        if not current_user.is_authenticated or not current_user.is_admin:
            # 如果不是，则中止请求并返回 403 Forbidden 错误
            abort(403)
        # 如果是管理员，则正常执行被装饰的视图函数
        return f(*args, **kwargs)
    return decorated_function

# --- 2. 创建 admin 蓝图 ---
# 创建一个名为 'admin' 的蓝图，所有属于此蓝图的路由都将以 /admin 为前缀
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# --- 3. 后台视图函数 ---

@admin_bp.route('/dashboard') # 仪表盘页面路由
@login_required # 要求用户必须登录
@admin_required # 要求用户必须是管理员
def dashboard():
    """
    为仪表盘页面 (dashboard.html) 提供数据。
    """
    # 查询并统计总用户数
    user_count = User.query.count()
    # 查询并统计总文章数
    post_count = Post.query.count()
    # 使用数据库的 SUM 函数计算所有文章的总浏览量，如果结果为 None（没有文章时），则默认为 0
    total_views = db.session.query(func.sum(Post.views)).scalar() or 0
    # 查询最新注册的 5 个用户，用于在仪表盘显示
    all_users = User.query.order_by(User.registration_date.desc()).limit(5).all()
    # 查询最新发布的 5 篇文章，用于在仪表盘显示
    all_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()

    # 渲染仪表盘模板，并将所有查询到的数据传递给前端
    return render_template(
        'admin/dashboard.html', 
        title='后台管理',
        user_count=user_count,
        post_count=post_count,
        active_page='dashboard', # 用于在侧边栏高亮“仪表盘”菜单
        total_views=total_views,
        users=all_users,
        posts=all_posts
    )

@admin_bp.route('/users') # 用户列表页面路由
@login_required
@admin_required
def user_list():
    """为独立的用户管理页面 (user_list.html) 提供数据"""
    # 查询所有用户，并按 ID 降序排列
    users = User.query.order_by(User.id.desc()).all()
    # 渲染用户列表模板
    return render_template('admin/user_list.html', title='用户管理', users=users, active_page='user_list')


@admin_bp.route('/users/<int:user_id>') # 用户详情页面路由
@login_required
@admin_required
def user_detail(user_id):
    """
    为用户详情页面 (user_detail.html) 提供数据。
    """
    # 根据 URL 中的 user_id 查询用户，如果找不到则自动返回 404 错误
    user = User.query.get_or_404(user_id)
    # 计算该特定用户所有文章的总浏览量
    user_total_views = db.session.query(func.sum(Post.views)).filter(Post.user_id == user.id).scalar() or 0
    # 渲染用户详情模板
    return render_template(
        'admin/user_detail.html',
        title=f"用户详情 - {user.username}",
        user=user,
        user_total_views=user_total_views,
        active_page='user_list' # 保持“用户管理”菜单高亮
    )

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST']) # 编辑用户信息的路由
@login_required
@admin_required
def edit_user(user_id):
    """
    处理管理员编辑用户信息的逻辑。
    支持 GET (显示表单) 和 POST (处理表单提交) 请求。
    """
    user_to_edit = User.query.get_or_404(user_id)
    # 实例化管理员专用的编辑表单，并传入原始用户信息用于验证
    form = AdminEditUserForm(original_user=user_to_edit)

    # 如果是 POST 请求且表单验证通过
    if form.validate_on_submit():
        # 将表单中的数据更新到用户对象
        user_to_edit.username = form.username.data
        user_to_edit.email = form.email.data
        user_to_edit.bio = form.bio.data
        user_to_edit.is_admin = form.is_admin.data
        
        # 如果管理员输入了新密码
        if form.password.data:
            # 对新密码进行哈希处理
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user_to_edit.password_hash = hashed_password
            flash('用户密码已更新。', 'info')

        # 提交数据库会话，保存所有更改
        db.session.commit()
        flash(f"用户 '{user_to_edit.username}' 的资料已成功更新！", 'success')
        # 操作成功后，重定向回该用户的详情页面
        return redirect(url_for('admin.user_detail', user_id=user_to_edit.id))

    # 如果是 GET 请求，用该用户的现有数据预填充表单
    elif request.method == 'GET':
        form.username.data = user_to_edit.username
        form.email.data = user_to_edit.email
        form.bio.data = user_to_edit.bio
        form.is_admin.data = user_to_edit.is_admin

    # 渲染编辑用户的模板
    return render_template(
        'admin/edit_user.html',
        title=f"编辑用户 - {user_to_edit.username}",
        form=form,
        user=user_to_edit
    )

@admin_bp.route('/posts') # 文章列表页面路由
@login_required
@admin_required
def post_list():
    """为独立的文章管理页面 (post_list.html) 提供数据"""
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    # 查询所有写过文章的作者，用于前端的筛选下拉菜单
    authors = User.query.join(Post, User.id == Post.user_id).distinct().all()
    
    return render_template('admin/post_list.html', title='文章管理', posts=posts, authors=authors, active_page='post_list')


# --- 4. 后台操作路由（示例） ---
# 这些路由处理具体的“动作”，比如删除

@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST']) # 删除文章的路由
@login_required
@admin_required
def delete_admin_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    flash(f"文章 '{post_to_delete.title}' 已被成功删除。", "success")
    return redirect(url_for('admin.post_list'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST']) # 删除用户的路由
@login_required
@admin_required
def delete_admin_user(user_id):
    # 防止管理员误删自己的账户
    if user_id == current_user.id:
        flash("不能删除当前登录的管理员账户。", "danger")
        return redirect(url_for('admin.user_list'))
        
    user_to_delete = User.query.get_or_404(user_id)
    # 重要：在删除用户前，应处理其关联的文章。这里直接删除。
    Post.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f"用户 '{user_to_delete.username}' 已被成功删除。", "success")
    return redirect(url_for('admin.user_list'))
