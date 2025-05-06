# Flask
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, IMAGES

# DB
from pymongo import MongoClient

# debug
from bson import ObjectId
from bson.errors import InvalidId

from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

client = MongoClient("mongodb://localhost:27017/")
db = client.news_feed
posts_collection = db.posts

# Настройка загрузки изображений
# Папка для сохранения
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads'  
# Разрешаем только изображения
app.config['UPLOADED_IMAGES_ALLOW'] = IMAGES  
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

# Создаём папку, если её нет
os.makedirs(app.config['UPLOADED_IMAGES_DEST'], exist_ok=True)


@app.route("/")
def news_feed():
    page = int(request.args.get('page', 1))
    per_page = 5
    
    # Получаем общее количество постов
    total_posts = posts_collection.count_documents({})
    
    # Вычисляем общее количество страниц
    total_pages = (total_posts + per_page - 1) // per_page
    
    posts = list(posts_collection.find()
               .sort("created_at", -1)
               .skip((page - 1) * per_page)
               .limit(per_page))
    
    return render_template("news_feed.html", 
                         posts=posts, 
                         page=page,
                         total_pages=total_pages)

@app.route("/post/<post_id>")
def view_post(post_id):
    try:
        post = posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            flash("Новость не найдена!", "error")
            return redirect(url_for("news_feed"))
        
        # Увеличиваем счетчик просмотров
        posts_collection.update_one(
            {"_id": ObjectId(post_id)}, 
            {"$inc": {"views": 1}}
        )
        
        return render_template("post_detail.html", post=post, page=0, total_pages=0)
    
    except InvalidId:
        flash("Неверный ID новости", "error")
        return redirect(url_for("news_feed"))
        

@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        author = request.form.get("author")
        tags = [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()]
        
        if not all([title, content, author]):
            flash("Заполните все обязательные поля!", "error")
            return redirect(url_for("create_post"))

        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                try:
                    filename = f"{datetime.now().timestamp()}_{secure_filename(image.filename)}"
                    image_path = f"uploads/{filename}"
                    images.save(image, name=filename)
                except Exception as e:
                    flash(f"Ошибка загрузки изображения: {e}", "error")
                    return redirect(url_for("create_post"))

        new_post = {
            "title": title,
            "content": content,
            "author": author,
            "tags": tags,
            "image": image_path,
            "created_at": datetime.utcnow(),
            "views": 0
        }
        posts_collection.insert_one(new_post)
        flash("Новость успешно добавлена!", "success")
        return redirect(url_for("news_feed"))

    return render_template("create_post.html")

@app.route("/delete_post/<post_id>", methods=["POST"])
def delete_post(post_id):
    try:
        # Проверяем, существует ли пост
        post = posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            flash("Пост не найден!", "error")
            return redirect(url_for("news_feed"))

        # Удаляем пост
        posts_collection.delete_one({"_id": ObjectId(post_id)})
        
        # Удаляем связанное изображение (если есть)
        if post.get('image'):
            try:
                os.remove(os.path.join(app.static_folder, post['image']))
            except OSError:
                pass  # Файл уже удален или не существует
        
        flash("Пост успешно удален!", "success")
    except InvalidId:
        flash("Неверный ID поста", "error")
    except Exception as e:
        flash(f"Ошибка при удалении: {str(e)}", "error")
    
    return redirect(url_for("news_feed"))

if __name__ == "__main__":
    app.run(debug=True)