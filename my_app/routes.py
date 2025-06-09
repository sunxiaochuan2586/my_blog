# my_app/routes.py
from flask import render_template, request, redirect, url_for, flash, abort, Blueprint
from my_app import db, bcrypt
from my_app.models import User, Post
from my_app.forms import RegistrationForm, LoginForm, PostForm
from flask_login import login_user, logout_user, current_user, login_required
from my_app.forms import  ChangePasswordForm

# 确保这里的变量名是 routes_bp
routes_bp = Blueprint('routes', __name__ )


@routes_bp.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts, title='博客首页')

@routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('routes.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('账户创建成功！现在可以登录了。', 'success')
        return redirect(url_for('routes.login'))
    
    return render_template('register.html', title='注册', form=form)

@routes_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
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
    """显示用户个人资料页面"""
    # Flask-Login 提供的 current_user 就是当前登录的用户对象
    # 我们可以直接把它传递给模板
    return render_template('profile.html', title='我的账户')

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
