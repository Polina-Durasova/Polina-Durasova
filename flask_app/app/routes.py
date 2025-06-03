from flask import render_template, flash, redirect, url_for, Blueprint, request
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, News
from app.forms import LoginForm, RegistrationForm, NewsForm, EditProfileForm
from datetime import datetime
from flask import current_app

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
@main_routes.route('/index')
def index():
    from app.models import News
    news = News.query.order_by(News.timestamp.desc()).all()
    from flask import render_template
    return render_template('index.html', title='Главная', news=news)

@app.route('/')
@app.route('/index')
def index():
    news = News.query.order_by(News.timestamp.desc()).all()
    return render_template('index.html', title='Главная', news=news)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный email или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, вы успешно зарегистрировались!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('Изменения сохранены.')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    return render_template('profile.html', title='Профиль', form=form)

@app.route('/news', methods=['GET', 'POST'])
@login_required
def news():
    form = NewsForm()
    if form.validate_on_submit():
        news = News(
            title=form.title.data,
            content=form.content.data,
            author=current_user)
        db.session.add(news)
        db.session.commit()
        flash('Новость опубликована!')
        return redirect(url_for('index'))
    return render_template('news.html', title='Добавить новость', form=form)

@app.route('/edit_news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    news = News.query.get_or_404(id)
    if news.author != current_user:
        abort(403)
    form = NewsForm()
    if form.validate_on_submit():
        news.title = form.title.data
        news.content = form.content.data
        db.session.commit()
        flash('Новость обновлена.')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.title.data = news.title
        form.content.data = news.content
    return render_template('edit_news.html', title='Редактировать новость', form=form)

@app.route('/delete_news/<int:id>', methods=['POST'])
@login_required
def delete_news(id):
    news = News.query.get_or_404(id)
    if news.author != current_user:
        abort(403)
    db.session.delete(news)
    db.session.commit()
    flash('Новость удалена.')
    return redirect(url_for('index'))