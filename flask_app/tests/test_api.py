import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_user_operations():
    # Создание пользователя
    user_data = {
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'email': 'ivan@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/users', json=user_data)
    print('Create user:', response.status_code, response.json())

    # Получение токена
    auth_data = {
        'email': 'ivan@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/tokens', auth=(auth_data['email'], auth_data['password']))
    token = response.json().get('token')
    print('Get token:', response.status_code, token)

    headers = {'Authorization': f'Bearer {token}'}

    # Получение информации о пользователе
    user_id = response.json().get('user_id')
    response = requests.get(f'{BASE_URL}/users/{user_id}', headers=headers)
    print('Get user:', response.status_code, response.json())

    # Обновление пользователя
    update_data = {'first_name': 'Иван Петрович'}
    response = requests.put(f'{BASE_URL}/users/{user_id}', json=update_data, headers=headers)
    print('Update user:', response.status_code, response.json())

def test_news_operations():
    # Получение токена
    auth_data = {
        'email': 'ivan@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/tokens', auth=(auth_data['email'], auth_data['password']))
    token = response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}

    # Создание новости
    news_data = {
        'title': 'Новая новость',
        'content': 'Содержание новости...'
    }
    response = requests.post(f'{BASE_URL}/news', json=news_data, headers=headers)
    print('Create news:', response.status_code, response.json())
    news_id = response.json().get('id')

    # Получение новости
    response = requests.get(f'{BASE_URL}/news/{news_id}', headers=headers)
    print('Get news:', response.status_code, response.json())

    # Обновление новости
    update_data = {'title': 'Обновленный заголовок'}
    response = requests.put(f'{BASE_URL}/news/{news_id}', json=update_data, headers=headers)
    print('Update news:', response.status_code, response.json())

    # Удаление новости
    response = requests.delete(f'{BASE_URL}/news/{news_id}', headers=headers)
    print('Delete news:', response.status_code)

if __name__ == '__main__':
    print("Testing user operations:")
    test_user_operations()
    
    print("\nTesting news operations:")
    test_news_operations()