# my_app/admin/routes.py

# --- 导入必要的模块 ---
from flask import Blueprint, render_template, abort
from flask_login import current_user
from my_app.models import User, Post
from my_app import db
from functools import wraps

# --- 1. 管理员权限装饰器 (你的版本已经很完美了) ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 增加一个对 is_authenticated 的检查，更严谨
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- 2. 创建 admin 蓝图 ---
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# --- 3. 为你的后台页面提供数据的路由函数 ---

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    为集成的仪表盘页面 (dashboard.html) 提供所有需要的数据。
    """
    # 查询统计数据
    user_count = User.query.count()
    post_count = Post.query.count()
    
    # 查询列表数据，用于在仪表盘上直接展示
    all_users = User.query.order_by(User.registration_date.desc()).limit(5).all() # 只取最新的5个用户
    all_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all() # 只取最新的5篇文章

    # '总浏览量' 是一个高级功能，我们暂时用一个假数据来填充
    total_views = post_count  

    # 把所有需要的数据一次性传递给 dashboard.html
    return render_template(
        'admin/dashboard.html', 
        title='后台管理',
        user_count=user_count,
        post_count=post_count,
        active_page='dashboard',
        total_views=total_views,
        users=all_users,  # 将用户列表传给模板
        posts=all_posts   # 将文章列表传给模板
        )


@admin_bp.route('/users')
@admin_required
def user_list():
    """为独立的用户管理页面 (user_list.html) 提供数据"""
    users = User.query.order_by(User.id.desc()).all()
    
    # user_list.html 模板中需要计算每个用户的文章数，
    # 但通过 user.posts 关系可以直接获取，所以不需要额外查询 posts
    return render_template('admin/user_list.html', title='用户管理', users=users,active_page='user_list')


@admin_bp.route('/posts')
@admin_required
def post_list():
    """为独立的文章管理页面 (post_list.html) 提供数据"""
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    
    # 为了作者筛选下拉菜单，我们需要获取所有发表过文章的用户作为作者
    # 使用 .join() 和 .distinct() 来确保只获取有文章的作者且不重复
    authors = User.query.join(Post, User.id == Post.user_id).distinct().all()
    
    return render_template('admin/post_list.html', title='文章管理', posts=posts, authors=authors,active_page='post_list')