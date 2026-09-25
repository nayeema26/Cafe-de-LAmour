# Café de L'Amour — Full-Stack Café Management

A beginner-friendly Flask + MongoDB CRUD management system using Bootstrap 5, Jinja2 and PyMongo.

## Stack
- HTML5, CSS3, vanilla JavaScript
- Bootstrap 5
- Flask + Jinja2
- MongoDB + PyMongo

## 1. Create the environment

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install packages
```bash
pip install -r requirements.txt
```

## 3. Configure MongoDB

Local MongoDB:
```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=cafe_de_lamour_db
SECRET_KEY=change-me
```

For MongoDB Atlas, replace `MONGO_URI` with the Atlas connection string. Never commit `.env`.

Copy `.env.example` to `.env`.

## 4. Seed sample data
```bash
python seed.py
```

## 5. Run Flask
```bash
python app.py
```

🌐 Live Demo: http://127.0.0.1:5000/

## Frontend → backend → database

Browser form → Flask route → validation → PyMongo → MongoDB → Flask/Jinja2 → HTML response.

For example, adding a dessert sends a POST request to `/menu/add`. Flask validates the form, inserts a document into `menu_items`, then redirects to `/menu`, where the latest documents are queried and rendered.

## Main routes
- `/` dashboard
- `/menu`
- `/menu/add`
- `/menu/edit/<id>`
- `/menu/delete/<id>`
- `/categories`
- `/categories/add`
- `/categories/edit/<id>`
- `/categories/delete/<id>`
- `/customers`
- `/customers/add`
- `/customers/edit/<id>`
- `/customers/delete/<id>`
- `/orders`
- `/orders/add`
- `/orders/<id>`
- `/orders/status/<id>`
- `/orders/delete/<id>`

## MongoDB collections
- `menu_items`
- `categories`
- `customers`
- `orders`

This is a student CRUD project. Authentication, payments, CSRF protection and production deployment hardening should be added before real-world use.
