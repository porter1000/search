from backend.models import db, User, InventoryItem, Page
import json
from fuzzywuzzy import process

def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

def get_user(username):
    return User.query.filter_by(username=username).first()

def authenticate_user(username, password):
    user = get_user(username)
    if user and user.check_password(password):
        return user
    return None

def update_preferences(user, preferences):
    user.preferences = json.dumps(preferences)
    db.session.commit()

def get_preferences(user):
    if user.preferences:
        return json.loads(user.preferences)
    return {}

def create_inventory_item(name, description, quantity):
    item = InventoryItem(name=name, description=description, quantity=quantity)
    db.session.add(item)
    db.session.commit()

def get_inventory_items():
    return InventoryItem.query.all()

def update_inventory_item(item_id, name, description, quantity):
    item = InventoryItem.query.get(item_id)
    item.name = name
    item.description = description
    item.quantity = quantity
    db.session.commit()

def delete_inventory_item(item_id):
    item = InventoryItem.query.get(item_id)
    db.session.delete(item)
    db.session.commit()

def search_pages(query, page, per_page):
    offset = (page - 1) * per_page
    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, content FROM pages WHERE content MATCH ? LIMIT ? OFFSET ?", (query, per_page, offset))
    results = cursor.fetchall()
    conn.close()
    return results

def fuzzy_search_pages(query, page, per_page):
    results = search_pages(query, page, per_page)
    if results:
        return results

    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, content FROM pages")
    pages = cursor.fetchall()
    conn.close()

    page_texts = {f"{url} {title}": (url, title, content) for url, title, content in pages}
    matched_texts = process.extract(query, page_texts.keys(), limit=per_page)
    fuzzy_results = [page_texts[text[0]] for text in matched_texts if text[1] > 70]
    return fuzzy_results
