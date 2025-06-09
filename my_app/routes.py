# my_app/routes.py
from flask import render_template, request, redirect, url_for, flash, abort, Blueprint
from my_app import db, bcrypt
from my_app.models import User, Post
from my_app.forms import RegistrationForm, LoginForm, PostForm
from flask_login import login_user, logout_user, current_user, login_required

# 确保这里的变量名是 routes_bp
routes_bp = Blueprint('routes', __name__)

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