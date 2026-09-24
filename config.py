import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "cafe_de_lamour_db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
