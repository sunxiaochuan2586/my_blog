# my_app/admin/routes.py

# --- 导入必要的模块 ---
from flask import Blueprint, render_template, abort, flash, redirect, url_for
from flask_login import current_user, login_required
from ..models import User, Post, db
from sqlalchemy import func
from functools import wraps

# --- 1. 管理员权限装饰器 ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- 2. 创建 admin 蓝图 ---
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# --- 3. 后台视图函数 ---

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """
    为集成的仪表盘页面 (dashboard.html) 提供所有需要的数据。
    """
    user_count = User.query.count()
    post_count = Post.query.count()
    total_views = db.session.query(func.sum(Post.views)).scalar() or 0
    
    # 查询列表数据，用于在仪表盘上直接展示
    all_users = User.query.order_by(User.registration_date.desc()).limit(5).all()
    all_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html', 
        title='后台管理',
        user_count=user_count,
        post_count=post_count,
        active_page='dashboard',
        total_views=total_views,
        users=all_users,
        posts=all_posts
    )

@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    """为独立的用户管理页面 (user_list.html) 提供数据"""
    users = User.query.order_by(User.id.desc()).all()
    return render_template('admin/user_list.html', title='用户管理', users=users, active_page='user_list')


# --- ▼▼▼ 关键修复：在这里添加了你缺失的用户详情路由 ▼▼▼ ---
@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """
    为用户详情页面 (user_detail.html) 提供数据。
    """
    user = User.query.get_or_404(user_id)
    # 计算该用户所有文章的总浏览量
    user_total_views = db.session.query(func.sum(Post.views)).filter(Post.user_id == user.id).scalar() or 0
    return render_template(
        'admin/user_detail.html',
        title=f"用户详情 - {user.username}",
        user=user,
        user_total_views=user_total_views,
        active_page='user_list' # 保持“用户管理”菜单项高亮
    )
# --- ▲▲▲ 关键修复结束 ▲▲▲ ---


@admin_bp.route('/posts')
@login_required
@admin_required
def post_list():
    """为独立的文章管理页面 (post_list.html) 提供数据"""
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    authors = User.query.join(Post, User.id == Post.user_id).distinct().all()
    
    return render_template('admin/post_list.html', title='文章管理', posts=posts, authors=authors, active_page='post_list')

# --- 4. 添加后台操作路由（示例） ---
# 以下是处理删除等操作的路由，你需要根据实际需求来实现

@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_admin_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    flash(f"文章 '{post_to_delete.title}' 已被成功删除。", "success")
    return redirect(url_for('admin.post_list'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_admin_user(user_id):
    if user_id == current_user.id:
        flash("不能删除当前登录的管理员账户。", "danger")
        return redirect(url_for('admin.user_list'))
        
    user_to_delete = User.query.get_or_404(user_id)
    # 删用户前需要处理其文章，此处仅作示例
    Post.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f"用户 '{user_to_delete.username}' 已被成功删除。", "success")
    return redirect(url_for('admin.user_list'))
