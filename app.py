from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# MongoDB configuration
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/pesti_link')
mongo = PyMongo(app)

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        # Check if user already exists
        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        # Hash password and create user
        hashed_password = generate_password_hash(password)
        user = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'user_type': user_type,
            'created_at': datetime.utcnow()
        }
        
        mongo.db.users.insert_one(user)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = mongo.db.users.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    user_type = session['user_type']
    
    if user_type == 'shop_owner':
        # Get products for this shop owner
        products = list(mongo.db.products.find({'shop_owner_id': session['user_id']}))
        return render_template('shop_dashboard.html', products=products)
    else:
        # Get recent notifications for farmers
        notifications = list(mongo.db.notifications.find().sort('created_at', -1).limit(10))
        return render_template('farmer_dashboard.html', notifications=notifications)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session or session['user_type'] != 'shop_owner':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                image_filename = save_uploaded_file(file)
                if not image_filename:
                    flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP images only.', 'error')
                    return render_template('add_product.html')
        
        product = {
            'name': request.form['name'],
            'specifications': request.form['specifications'],
            'cost': float(request.form['cost']),
            'quantity': int(request.form['quantity']),
            'crop_type': request.form['crop_type'],
            'chemicals': request.form['chemicals'],
            'shop_owner_id': session['user_id'],
            'shop_name': session['username'],
            'image_filename': image_filename,
            'created_at': datetime.utcnow()
        }
        
        mongo.db.products.insert_one(product)
        
        # Create notification for farmers
        notification = {
            'type': 'new_product',
            'title': f'New Product: {product["name"]}',
            'message': f'{product["name"]} is now available at {product["shop_name"]}',
            'product_id': str(product['_id']),
            'created_at': datetime.utcnow()
        }
        mongo.db.notifications.insert_one(notification)
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_product.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session or session['user_type'] != 'shop_owner':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))
    
    product = mongo.db.products.find_one({'_id': ObjectId(product_id), 'shop_owner_id': session['user_id']})
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Handle file upload
        image_filename = product.get('image_filename')  # Keep existing image by default
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                new_image_filename = save_uploaded_file(file)
                if new_image_filename:
                    # Delete old image if it exists
                    if image_filename:
                        old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    image_filename = new_image_filename
                else:
                    flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP images only.', 'error')
                    return render_template('edit_product.html', product=product)
        
        # Update product
        update_data = {
            'name': request.form['name'],
            'specifications': request.form['specifications'],
            'cost': float(request.form['cost']),
            'quantity': int(request.form['quantity']),
            'crop_type': request.form['crop_type'],
            'chemicals': request.form['chemicals'],
            'image_filename': image_filename,
            'updated_at': datetime.utcnow()
        }
        
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)}, 
            {'$set': update_data}
        )
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    if 'user_id' not in session or session['user_type'] != 'shop_owner':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))
    
    product = mongo.db.products.find_one({'_id': ObjectId(product_id), 'shop_owner_id': session['user_id']})
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Delete associated image file
    if product.get('image_filename'):
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image_filename'])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Delete product from database
    mongo.db.products.delete_one({'_id': ObjectId(product_id)})
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/search')
def search():
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    query = request.args.get('q', '')
    crop_type = request.args.get('crop_type', '')
    
    search_filter = {}
    if query:
        search_filter['name'] = {'$regex': query, '$options': 'i'}
    if crop_type:
        search_filter['crop_type'] = {'$regex': crop_type, '$options': 'i'}
    
    products = list(mongo.db.products.find(search_filter))
    return render_template('search.html', products=products, query=query, crop_type=crop_type)

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    notifications = list(mongo.db.notifications.find().sort('created_at', -1))
    return render_template('notifications.html', notifications=notifications)

# Order routes
@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        flash('Access denied! Only farmers can place orders.', 'error')
        return redirect(url_for('login'))
    
    try:
        # Get form data
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        delivery_address = request.form['delivery_address']
        contact_number = request.form['contact_number']
        order_notes = request.form.get('order_notes', '')
        
        # Get product details
        product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('search'))
        
        # Check if enough quantity is available
        if quantity > product['quantity']:
            flash(f'Only {product["quantity"]} units available!', 'error')
            return redirect(url_for('search'))
        
        # Calculate total amount
        total_amount = quantity * product['cost']
        
        # Create order
        order = {
            'order_id': str(uuid.uuid4())[:8].upper(),  # Short order ID
            'farmer_id': session['user_id'],
            'farmer_name': session['username'],
            'product_id': product_id,
            'product_name': product['name'],
            'shop_owner_id': product['shop_owner_id'],
            'shop_name': product['shop_name'],
            'quantity': quantity,
            'unit_price': product['cost'],
            'total_amount': total_amount,
            'delivery_address': delivery_address,
            'contact_number': contact_number,
            'order_notes': order_notes,
            'status': 'pending',  # pending, confirmed, shipped, delivered, cancelled
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert order
        result = mongo.db.orders.insert_one(order)
        order['_id'] = result.inserted_id
        
        # Update product quantity
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$inc': {'quantity': -quantity}}
        )
        
        # Create notification for shop owner
        notification = {
            'type': 'new_order',
            'title': f'New Order: {product["name"]}',
            'message': f'Order #{order["order_id"]}: {quantity} units of {product["name"]} ordered by {session["username"]}',
            'order_id': str(order['_id']),
            'shop_owner_id': product['shop_owner_id'],
            'created_at': datetime.utcnow()
        }
        mongo.db.notifications.insert_one(notification)
        
        flash(f'Order placed successfully! Order ID: {order["order_id"]}', 'success')
        return redirect(url_for('order_confirmation', order_id=order['order_id']))
        
    except Exception as e:
        print(f"Order error: {e}")
        flash('Error placing order. Please try again.', 'error')
        return redirect(url_for('search'))

@app.route('/order_confirmation/<order_id>')
def order_confirmation(order_id):
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    order = mongo.db.orders.find_one({'order_id': order_id, 'farmer_id': session['user_id']})
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('search'))
    
    return render_template('order_confirmation.html', order=order)

@app.route('/my_orders')
def my_orders():
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    if session['user_type'] == 'farmer':
        orders = list(mongo.db.orders.find({'farmer_id': session['user_id']}).sort('created_at', -1))
    else:
        orders = list(mongo.db.orders.find({'shop_owner_id': session['user_id']}).sort('created_at', -1))
    
    # Convert ObjectId to string for JSON serialization
    for order in orders:
        order['_id'] = str(order['_id'])
        if 'product_id' in order:
            order['product_id'] = str(order['product_id'])
    
    return render_template('my_orders.html', orders=orders)

@app.route('/update_order_status/<order_id>', methods=['POST'])
def update_order_status(order_id):
    if 'user_id' not in session or session['user_type'] != 'shop_owner':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))
    
    order = mongo.db.orders.find_one({'_id': ObjectId(order_id), 'shop_owner_id': session['user_id']})
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('my_orders'))
    
    new_status = request.form['status']
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    
    if new_status not in valid_statuses:
        flash('Invalid status!', 'error')
        return redirect(url_for('my_orders'))
    
    # Update order status
    mongo.db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {'$set': {'status': new_status, 'updated_at': datetime.utcnow()}}
    )
    
    # Create notification for farmer
    notification = {
        'type': 'order_update',
        'title': f'Order #{order["order_id"]} Update',
        'message': f'Your order status has been updated to: {new_status.title()}',
        'order_id': str(order['_id']),
        'farmer_id': order['farmer_id'],
        'created_at': datetime.utcnow()
    }
    mongo.db.notifications.insert_one(notification)
    
    flash(f'Order status updated to {new_status.title()}!', 'success')
    return redirect(url_for('my_orders'))

if __name__ == '__main__':
    app.run(debug=True)
