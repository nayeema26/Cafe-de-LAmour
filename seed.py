from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client[os.getenv("DB_NAME", "cafe_de_lamour_db")]

categories = db["categories"]
menu = db["menu_items"]
customers = db["customers"]

category_names = ["Cakes", "Brownies", "Chocolates", "Ice Cream", "Beverages", "Waffles", "Cheesecakes", "Donuts"]
for name in category_names:
    categories.update_one({"name": name}, {"$setOnInsert": {"name": name, "description": f"Lovely {name.lower()} at Café de L'Amour."}}, upsert=True)

samples = [
    ("Chocolate Brownie", "Brownies", "Warm fudgy brownie with premium cocoa.", 180),
    ("Belgian Chocolate Cake", "Cakes", "Rich layered cake with Belgian chocolate.", 260),
    ("Chocolate Fudge", "Chocolates", "Silky house-made chocolate fudge.", 150),
    ("Brownie with Ice Cream", "Ice Cream", "Warm brownie served with vanilla ice cream.", 240),
    ("Chocolate Milkshake", "Beverages", "Creamy chocolate milkshake.", 190),
    ("Hot Chocolate", "Beverages", "Velvety hot chocolate finished with cocoa.", 160),
    ("Classic Cheesecake", "Cheesecakes", "Creamy cheesecake with a biscuit base.", 220),
    ("Belgian Waffle", "Waffles", "Golden waffle with chocolate drizzle.", 210),
]
for name, category, description, price in samples:
    menu.update_one({"name": name}, {"$setOnInsert": {
        "name": name, "category": category, "description": description,
        "price": price, "image_url": "", "available": True, "created_at": datetime.utcnow()
    }}, upsert=True)

customers.update_one({"email": "demo@cafedelamour.local"}, {"$setOnInsert": {
    "name": "Demo Guest", "email": "demo@cafedelamour.local", "phone": "9876543210",
    "address": "Café de L'Amour", "created_at": datetime.utcnow()
}}, upsert=True)

print("Seed completed without duplicating existing sample records.")
