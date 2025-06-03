from flask import jsonify, request, url_for, abort  # Flask-инструменты
from app import db  # База данных
from app.models import User, News  # Модели данных
from app.api import bp  # Blueprint для API
from app.api.auth import token_auth  # Аутентификация
from app.api.errors import bad_request  # Обработка ошибок

@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required  # Требуется авторизация
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())  # Возвращает данные пользователя в JSON

@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)  # Номер страницы
    per_page = min(request.args.get('per_page', 10, type=int), 100)  # Записей на страницу
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)  # JSON с пользователями

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    # Проверка обязательных полей
    if not all(field in data for field in ['first_name', 'last_name', 'email', 'password']):
        return bad_request('Необходимо указать имя, фамилию, email и пароль')
    # Проверка уникальности email
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Пользователь с таким email уже существует')
    # Создание и сохранение пользователя
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    # Ответ с кодом 201 (Created)
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    # Проверка прав доступа
    if token_auth.current_user().id != id:
        abort(403)  # 403 Forbidden
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    # Проверка email на уникальность
    if 'email' in data and data['email'] != user.email and User.query.filter_by(email=data['email']).first():
        return bad_request('Пользователь с таким email уже существует')
    # Обновление данных
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())

@bp.route('/news', methods=['GET'])
def get_news():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = News.to_collection_dict(News.query, page, per_page, 'api.get_news')
    return jsonify(data)

@bp.route('/news', methods=['POST'])
@token_auth.login_required
def create_news():
    data = request.get_json() or {}
    if 'title' not in data or 'content' not in data:
        return bad_request('Необходимо указать заголовок и содержание новости')
    news = News(author=token_auth.current_user())
    news.from_dict(data)
    db.session.add(news)
    db.session.commit()
    response = jsonify(news.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_news_item', id=news.id)
    return response

@bp.route('/news/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_news(id):
    news = News.query.get_or_404(id)
    # Проверка, что пользователь — автор новости
    if news.author != token_auth.current_user():
        abort(403)
    db.session.delete(news)
    db.session.commit()
    return '', 204  # 204 No Content