import os
import requests
from pymongo import MongoClient
from datetime import datetime

# Настройка подключения
client = MongoClient("mongodb://localhost:27017/")
db = client.news_feed
posts_collection = db.posts

# Создаем папку для изображений
os.makedirs("static/uploads/manual", exist_ok=True)

# Удаляем старые демо-новости
posts_collection.delete_many({"tags": "manual_demo"})

# 5 реальных новостей о разработке с работающими изображениями
demo_posts = [
    {
        "title": "Python 3.12 выходит с новым оптимизатором производительности",
        "content": "Новая версия Python 3.12 приносит значительные улучшения производительности, включая новый оптимизатор кода. По предварительным тестам, некоторые операции стали быстрее на 15-20%.",
        "author": "Иван Петров",
        "tags": ["python", "программирование", "новости", "manual_demo"],
        "image": "https://cdn.bulldogjob.com/system/readables/covers/000/004/109/max_res/21023_python_3.12.png",
        "views": 342
    },
    {
        "title": "Искусственный интеллект научился писать код на уровне джуниор-разработчика",
        "content": "Новая версия GitHub Copilot X демонстрирует поразительные результаты в генерации кода. Тестирование показало, что ИИ может решать 85% задач уровня junior-разработчика.",
        "author": "Анна Сидорова",
        "tags": ["искусственный интеллект", "github", "manual_demo"],
        "image": "https://th.bing.com/th/id/OIP.Qj_m0dJz7g80r3onLDgEPgHaDt?rs=1&pid=ImgDetMain",
        "views": 587
    },
    {
        "title": "Flutter 3.10: новые возможности для кроссплатформенной разработки",
        "content": "Google выпустил обновление Flutter 3.10 с поддержкой новых платформ и улучшенной производительностью на iOS-устройствах.",
        "author": "Максим Иванов",
        "tags": ["flutter", "мобильная разработка", "google", "manual_demo"],
        "image": "https://framerusercontent.com/images/zlbKRoHgjKuoktRl2G7VGTqwMdg.png",
        "views": 231
    },
    {
        "title": "Революция в веб-разработке: HTMX набирает популярность",
        "content": "Библиотека HTMX позволяет создавать современные веб-приложения без сложных JavaScript-фреймворков. Разработчики отмечают простоту интеграции и высокую скорость работы.",
        "author": "Елена Кузнецова",
        "tags": ["веб-разработка", "javascript", "manual_demo"],
        "image": "https://248006.selcdn.ru/main/iblock/17c/17c20ee605bed8319a56ccffc7418be1/633570a8b996fd5de505635182dc07fa.png",
        "views": 412
    },
    {
        "title": "Rust становится самым любимым языком программирования 5 год подряд",
        "content": "Согласно опросу StackOverflow, Rust сохраняет позицию самого любимого языка среди разработчиков благодаря своей безопасности и производительности.",
        "author": "Алексей Смирнов",
        "tags": ["rust", "программирование", "manual_demo"],
        "image": "https://litslink.com/wp-content/uploads/2022/04/photo_2022-04-26_17-25-06-1024x710.jpg",
        "views": 378
    }
]

def download_image(url, filename):
    """Загрузка и сохранение изображения"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        with open(f"static/uploads/manual/{filename}", 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
                
        return f"uploads/manual/{filename}"
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return None

# Загружаем и создаем посты
for i, post_data in enumerate(demo_posts):
    # Скачиваем изображение
    filename = f"post_{i+1}.jpg"
    image_path = download_image(post_data['image'], filename)
    
    if not image_path:
        print(f"Не удалось загрузить изображение для поста {i+1}")
        continue
    
    # Создаем документ для MongoDB
    post = {
        "title": post_data["title"],
        "content": post_data["content"],
        "author": post_data["author"],
        "tags": post_data["tags"],
        "image": image_path,
        "created_at": datetime.now(),
        "views": post_data["views"]
    }
    
    # Сохраняем в базу данных
    posts_collection.insert_one(post)
    print(f"Добавлен пост: {post_data['title']}")


print("Готово! База данных заполнена 5 реальными новостями.")