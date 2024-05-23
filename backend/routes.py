from flask import Flask, request, jsonify, session
from backend.database import init_db, db
from backend.services import create_user, authenticate_user, update_preferences, get_preferences, fuzzy_search_pages, create_inventory_item, get_inventory_items, update_inventory_item, delete_inventory_item
from flask_mail import Mail, Message
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../crawler.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
init_db(app)

@app.route('/api/configure_mail', methods=['POST'])
def configure_mail():
    data = request.json
    app.config.update(
        MAIL_SERVER=data.get('mail_server', 'smtp.example.com'),
        MAIL_PORT=data.get('mail_port', 587),
        MAIL_USERNAME=data['mail_username'],
        MAIL_PASSWORD=data['mail_password'],
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False
    )
    mail.init_app(app)
    return jsonify({'message': 'Mail configuration updated successfully'}), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    create_user(data['username'], data['email'], data['password'])
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = authenticate_user(data['username'], data['password'])
    if user:
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/preferences', methods=['GET', 'POST'])
def preferences():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        data = request.json
        update_preferences(user, data)
        return jsonify({'message': 'Preferences updated'})
    
    return jsonify(get_preferences(user))

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    results = fuzzy_search_pages(query, page, per_page)
    return jsonify(results)

@app.route('/api/send_email', methods=['POST'])
def send_email():
    data = request.json
    msg = Message(data['subject'], sender=app.config['MAIL_USERNAME'], recipients=[data['recipient']])
    msg.body = data['message']
    mail.send(msg)
    return jsonify({'message': 'Email sent successfully'}), 200

@app.route('/api/inventory', methods=['POST'])
def add_inventory_item():
    data = request.json
    create_inventory_item(data['name'], data['description'], data['quantity'])
    return jsonify({'message': 'Inventory item created successfully'}), 201

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    items = get_inventory_items()
    return jsonify([{'id': item.id, 'name': item.name, 'description': item.description, 'quantity': item.quantity} for item in items])

@app.route('/api/inventory/<int:item_id>', methods=['PUT'])
def update_inventory(item_id):
    data = request.json
    update_inventory_item(item_id, data['name'], data['description'], data['quantity'])
    return jsonify({'message': 'Inventory item updated successfully'}), 200

@app.route('/api/inventory/<int:item_id>', methods=['DELETE'])
def delete_inventory(item_id):
    delete_inventory_item(item_id)
    return jsonify({'message': 'Inventory item deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
