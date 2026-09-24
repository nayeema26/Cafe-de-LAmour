from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "cafe_de_lamour_db")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
db = client[DB_NAME]
menu_items = db["menu_items"]
categories = db["categories"]
customers = db["customers"]
orders = db["orders"]


def oid(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def safe_float(value):
    try:
        number = float(value)
        return number if number >= 0 else None
    except (TypeError, ValueError):
        return None


def dashboard_data():
    revenue = list(orders.aggregate([
        {"$match": {"status": {"$ne": "Cancelled"}}},
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]))
    return {
        "menu_count": menu_items.count_documents({}),
        "category_count": categories.count_documents({}),
        "customer_count": customers.count_documents({}),
        "order_count": orders.count_documents({}),
        "revenue": revenue[0]["total"] if revenue else 0,
        "pending": orders.count_documents({"status": "Pending"}),
        "completed": orders.count_documents({"status": "Completed"}),
        "recent_orders": list(orders.find().sort("order_date", -1).limit(6)),
    }


@app.route("/")
def index():
    try:
        data = dashboard_data()
        return render_template("index.html", **data)
    except PyMongoError:
        flash("Could not connect to MongoDB. Check your MONGO_URI and make sure MongoDB is running.", "danger")
        return render_template("index.html", menu_count=0, category_count=0, customer_count=0,
                               order_count=0, revenue=0, pending=0, completed=0, recent_orders=[])


@app.route("/dashboard")
def dashboard():
    return redirect(url_for("index"))


@app.route("/menu")
def menu():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    query = {}
    if q:
        query["$or"] = [{"name": {"$regex": q, "$options": "i"}},
                        {"description": {"$regex": q, "$options": "i"}}]
    if category:
        query["category"] = category
    return render_template("menu/list.html",
                           items=list(menu_items.find(query).sort("created_at", -1)),
                           categories=list(categories.find().sort("name", 1)),
                           q=q, selected_category=category)


@app.route("/menu/add", methods=["GET", "POST"])
def menu_add():
    cats = list(categories.find().sort("name", 1))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        price = safe_float(request.form.get("price"))
        if not name or not category or price is None or price <= 0:
            flash("Name, category and a positive price are required.", "warning")
            return render_template("menu/form.html", item=request.form, categories=cats, title="Add Menu Item")
        menu_items.insert_one({
            "name": name, "category": category,
            "description": request.form.get("description", "").strip(),
            "price": price, "image_url": request.form.get("image_url", "").strip(),
            "available": request.form.get("available") == "on",
            "created_at": datetime.utcnow()
        })
        flash("Menu item added.", "success")
        return redirect(url_for("menu"))
    return render_template("menu/form.html", item={}, categories=cats, title="Add Menu Item")


@app.route("/menu/edit/<id>", methods=["GET", "POST"])
def menu_edit(id):
    item_id = oid(id)
    if not item_id:
        flash("Invalid menu item ID.", "danger")
        return redirect(url_for("menu"))
    item = menu_items.find_one({"_id": item_id})
    if not item:
        flash("Menu item not found.", "warning")
        return redirect(url_for("menu"))
    cats = list(categories.find().sort("name", 1))
    if request.method == "POST":
        price = safe_float(request.form.get("price"))
        if not request.form.get("name", "").strip() or price is None or price <= 0:
            flash("Name and a positive price are required.", "warning")
            return render_template("menu/form.html", item={**item, **request.form}, categories=cats, title="Edit Menu Item")
        menu_items.update_one({"_id": item_id}, {"$set": {
            "name": request.form.get("name", "").strip(),
            "category": request.form.get("category", "").strip(),
            "description": request.form.get("description", "").strip(),
            "price": price,
            "image_url": request.form.get("image_url", "").strip(),
            "available": request.form.get("available") == "on"
        }})
        flash("Menu item updated.", "success")
        return redirect(url_for("menu"))
    return render_template("menu/form.html", item=item, categories=cats, title="Edit Menu Item")


@app.post("/menu/delete/<id>")
def menu_delete(id):
    item_id = oid(id)
    if item_id:
        menu_items.delete_one({"_id": item_id})
        flash("Menu item deleted.", "success")
    else:
        flash("Invalid menu item ID.", "danger")
    return redirect(url_for("menu"))


@app.route("/categories")
def category_list():
    return render_template("categories/list.html", categories=list(categories.find().sort("name", 1)))


@app.route("/categories/add", methods=["GET", "POST"])
def category_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Category name is required.", "warning")
        else:
            categories.insert_one({"name": name, "description": request.form.get("description", "").strip()})
            flash("Category added.", "success")
            return redirect(url_for("category_list"))
    return render_template("categories/form.html", category={}, title="Add Category")


@app.route("/categories/edit/<id>", methods=["GET", "POST"])
def category_edit(id):
    category_id = oid(id)
    category = categories.find_one({"_id": category_id}) if category_id else None
    if not category:
        flash("Category not found.", "warning")
        return redirect(url_for("category_list"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Category name is required.", "warning")
        else:
            categories.update_one({"_id": category_id}, {"$set": {
                "name": name, "description": request.form.get("description", "").strip()
            }})
            flash("Category updated.", "success")
            return redirect(url_for("category_list"))
    return render_template("categories/form.html", category=category, title="Edit Category")


@app.post("/categories/delete/<id>")
def category_delete(id):
    category_id = oid(id)
    if category_id:
        categories.delete_one({"_id": category_id})
        flash("Category deleted.", "success")
    return redirect(url_for("category_list"))


@app.route("/customers")
def customer_list():
    q = request.args.get("q", "").strip()
    query = {"$or": [{"name": {"$regex": q, "$options": "i"}},
                     {"email": {"$regex": q, "$options": "i"}},
                     {"phone": {"$regex": q, "$options": "i"}}]} if q else {}
    return render_template("customers/list.html", customers=list(customers.find(query).sort("created_at", -1)), q=q)


@app.route("/customers/add", methods=["GET", "POST"])
def customer_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        if not name or "@" not in email or not phone:
            flash("Name, valid email and phone are required.", "warning")
            return render_template("customers/form.html", customer=request.form, title="Add Customer")
        customers.insert_one({"name": name, "email": email, "phone": phone,
                              "address": request.form.get("address", "").strip(),
                              "created_at": datetime.utcnow()})
        flash("Customer added.", "success")
        return redirect(url_for("customer_list"))
    return render_template("customers/form.html", customer={}, title="Add Customer")


@app.route("/customers/edit/<id>", methods=["GET", "POST"])
def customer_edit(id):
    customer_id = oid(id)
    customer = customers.find_one({"_id": customer_id}) if customer_id else None
    if not customer:
        flash("Customer not found.", "warning")
        return redirect(url_for("customer_list"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        if not name or "@" not in email or not phone:
            flash("Name, valid email and phone are required.", "warning")
            return render_template("customers/form.html", customer={**customer, **request.form}, title="Edit Customer")
        customers.update_one({"_id": customer_id}, {"$set": {
            "name": name, "email": email, "phone": phone,
            "address": request.form.get("address", "").strip()
        }})
        flash("Customer updated.", "success")
        return redirect(url_for("customer_list"))
    return render_template("customers/form.html", customer=customer, title="Edit Customer")


@app.post("/customers/delete/<id>")
def customer_delete(id):
    customer_id = oid(id)
    if customer_id:
        customers.delete_one({"_id": customer_id})
        flash("Customer deleted.", "success")
    return redirect(url_for("customer_list"))


@app.route("/orders")
def order_list():
    return render_template("orders/list.html", orders=list(orders.find().sort("order_date", -1)))


@app.route("/orders/add", methods=["GET", "POST"])
def order_add():
    customers_list = list(customers.find().sort("name", 1))
    items = list(menu_items.find({"available": True}).sort("name", 1))
    if request.method == "POST":
        customer_id = oid(request.form.get("customer_id"))
        selected_ids = request.form.getlist("item_id")
        quantities = request.form.getlist("quantity")
        customer = customers.find_one({"_id": customer_id}) if customer_id else None
        ordered = []
        total = 0
        for item_id, qty_raw in zip(selected_ids, quantities):
            item = menu_items.find_one({"_id": oid(item_id)}) if oid(item_id) else None
            try:
                qty = int(qty_raw)
            except ValueError:
                qty = 0
            if item and qty > 0:
                line_total = item["price"] * qty
                ordered.append({"item_id": item["_id"], "name": item["name"],
                                "price": item["price"], "quantity": qty, "line_total": line_total})
                total += line_total
        if not customer or not ordered:
            flash("Select a customer and at least one menu item.", "warning")
            return render_template("orders/form.html", customers=customers_list, items=items)
        orders.insert_one({"customer_id": customer["_id"], "customer_name": customer["name"],
                           "items": ordered, "total_amount": total, "status": "Pending",
                           "order_date": datetime.utcnow()})
        flash("Order created.", "success")
        return redirect(url_for("order_list"))
    return render_template("orders/form.html", customers=customers_list, items=items)


@app.route("/orders/<id>")
def order_view(id):
    order_id = oid(id)
    order = orders.find_one({"_id": order_id}) if order_id else None
    if not order:
        flash("Order not found.", "warning")
        return redirect(url_for("order_list"))
    return render_template("orders/view.html", order=order)


@app.post("/orders/status/<id>")
def order_status(id):
    order_id = oid(id)
    status = request.form.get("status")
    allowed = {"Pending", "Preparing", "Ready", "Completed", "Cancelled"}
    if order_id and status in allowed:
        orders.update_one({"_id": order_id}, {"$set": {"status": status}})
        flash("Order status updated.", "success")
    return redirect(url_for("order_list"))


@app.post("/orders/delete/<id>")
def order_delete(id):
    order_id = oid(id)
    if order_id:
        orders.delete_one({"_id": order_id})
        flash("Order deleted.", "success")
    return redirect(url_for("order_list"))


if __name__ == "__main__":
    app.run(debug=True)
