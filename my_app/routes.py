# my_app/routes.py
from flask import render_template, request, redirect, url_for, flash, abort, Blueprint
from my_app import db, bcrypt
from my_app.models import User, Post
from my_app.forms import RegistrationForm, LoginForm, PostForm
from flask_login import login_user, logout_user, current_user, login_required
from my_app.forms import  ChangePasswordForm
from sqlalchemy import func # <-- 导入 func
from .forms import EditProfileForm # 导入刚刚创建的表单
import hashlib # 用于计算 MD5

# 确保这里的变量名是 routes_bp
routes_bp = Blueprint('routes', __name__ )


@routes_bp.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts, title='博客首页')

@routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: 
        return redirect(url_for('routes.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        
        # --- 新增逻辑：在创建用户时生成 avatar_hash ---
        if user.email:
            email_hash = hashlib.md5(user.email.lower().encode('utf-8')).hexdigest()
            user.avatar_hash = email_hash
        # --- 逻辑结束 ---

        db.session.add(user)
        db.session.commit()
        
        flash('账户创建成功！现在可以登录了。', 'success')
        return redirect(url_for('routes.login'))
    
    return render_template('register.html', title='注册', form=form)


@routes_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: 
        return redirect(url_for('routes.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            
            # --- 新增逻辑：在用户登录时检查并补充 avatar_hash ---
            if user.avatar_hash is None and user.email:
                email_hash = hashlib.md5(user.email.lower().encode('utf-8')).hexdigest()
                user.avatar_hash = email_hash
                db.session.commit()
            # --- 逻辑结束 ---

            next_page = request.args.get('next')
            flash('登录成功！', 'success')
            return redirect(next_page) if next_page else redirect(url_for('routes.index'))
        else:
            flash('登录失败，请检查邮箱和密码。', 'danger')
            
    return render_template('login.html', title='登录', form=form)
@routes_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('文章创建成功！', 'success')
        return redirect(url_for('routes.index'))
    return render_template('create_post.html', title='创建新文章', form=form)

@routes_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@routes_bp.route('/post/<int:post_id>')
def post_detail(post_id: int):
    post = Post.query.get_or_404(post_id)    
    if post.views is None:
        post.views = 0
    post.views += 1  # 使用更简洁的 += 语法
    db.session.commit()
    return render_template('post_detail.html', post=post, title=post.title)





@routes_bp.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('文章更新成功！', 'success')
        return redirect(url_for('routes.post_detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    
    # ▼▼▼ 核心修改 ▼▼▼
    # 将 post 对象传递给模板，以便我们能获取 post.id 作为草稿的唯一键
    return render_template('create_post.html', title='更新文章', form=form, post=post)


@routes_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('文章已删除。', 'success')
    return redirect(url_for('routes.index'))    

@routes_bp.context_processor
def inject_recent_posts():
    """
    将最新的5篇文章注入到所有模板的上下文中。
    """
    recent_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()
    return dict(recent_posts=recent_posts)

@routes_bp.route('/profile')
@login_required
def profile():
    """
    个人资料页视图函数。
    需要计算并传递该用户所有文章的总浏览量。
    """
    # 查询当前用户的所有文章
    posts = Post.query.filter_by(author=current_user).order_by(Post.date_posted.desc()).all()
    
    # 使用数据库函数 sum() 来高效计算总浏览量
    # .scalar() 会返回查询结果的第一列的第一行，如果没有结果则返回 None
    total_views = db.session.query(func.sum(Post.views)).filter_by(author=current_user).scalar()
    
    # 如果用户还没有任何文章或浏览量，total_views 可能为 None，我们将其设为 0
    if total_views is None:
        total_views = 0

    return render_template('profile.html', 
                           title='我的账户', 
                           posts=posts, 
                           total_views=total_views)

@routes_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # 1. 验证用户输入的“当前密码”是否正确
        if bcrypt.check_password_hash(current_user.password_hash, form.current_password.data):
            # 2. 如果正确，就设置新密码
            new_hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password_hash = new_hashed_password
            db.session.commit()
            flash('密码修改成功！', 'success')
            return redirect(url_for('routes.profile')) # 修改成功后，跳回到个人资料页
        else:
            # 3. 如果“当前密码”不正确，就给出提示
            flash('当前密码不正确，请重试。', 'danger')
    return render_template('change_password.html', title='修改密码', form=form)


@routes_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    
    if form.validate_on_submit():
        # --- 处理表单提交 ---
        current_user.bio = form.bio.data
        current_user.github_url = form.github_url.data
        current_user.website_url = form.website_url.data
        
        # 计算并保存 email 的 MD5 hash 用于 Gravatar
        if current_user.email:
            email_hash = hashlib.md5(current_user.email.lower().encode('utf-8')).hexdigest()
            current_user.avatar_hash = email_hash

        db.session.commit()
        flash('你的个人资料已更新！', 'success')
        return redirect(url_for('routes.profile')) # 更新后重定向回个人资料页

    elif request.method == 'GET':
        # --- 预填充表单的当前数据 ---
        form.bio.data = current_user.bio
        form.github_url.data = current_user.github_url
        form.website_url.data = current_user.website_url
        
    return render_template('edit_profile.html', title='编辑资料', form=form)