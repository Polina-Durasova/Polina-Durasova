from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.news_feed
posts_collection = db.posts

# Удалить ВСЕ документы из коллекции
result = posts_collection.delete_many({})
print(f"Удалено {result.deleted_count} документов")