from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

users = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['loginName']
        password = request.form['loginPassword']
        if name in users and users[name]['password'] == password:
            session['username'] = name
            flash('Logged in successfully!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!')
            return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['signupName']
    password = request.form['signupPassword']
    phone = request.form['signupPhone']

    if name in users:
        flash('User already exists!')
    else:
        users[name] = {'password': password, 'phone': phone}
        flash('Sign up successful! Please login.')
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'username' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    return render_template('home.html', username=session['username'])

@app.route('/sale', methods=['GET', 'POST'])
def sale():
    if 'username' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        category = request.form['category']
        item_name = request.form['itemName']
        expiry = request.form['expiryDate']
        rate = request.form['rate']
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            conn = sqlite3.connect('database.db')
            conn.execute("INSERT INTO items (name, category, expiry, price, image) VALUES (?, ?, ?, ?, ?)",
                         (item_name, category, expiry, rate, filename))
            conn.commit()
            conn.close()

            flash('Item added successfully!')
        else:
            flash('Invalid image file!')

        return redirect(url_for('sale'))

    return render_template('sale.html')

@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if 'username' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Receiving item details from the hidden fields
        item_name = request.form.get('item_name')
        category = request.form.get('category')
        expiry = request.form.get('expiry')
        rate = request.form.get('rate')
        image = request.form.get('image')

        item = {
            'item_name': item_name,
            'category': category,
            'expiry': expiry,
            'rate': rate,
            'image': image
        }

        return render_template('order.html', item=item)

    # Display items
    conn = sqlite3.connect('database.db')
    cursor = conn.execute("SELECT name, category, expiry, price, image FROM items")
    items = cursor.fetchall()  # returns list of tuples
    conn.close()

    return render_template('buy.html', items=items)

@app.route('/order', methods=['POST'])
def order():
    if 'username' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    # Receiving item data via form POST
    item_name = request.form.get('item_name')
    category = request.form.get('category')
    expiry = request.form.get('expiry')
    rate = request.form.get('rate')
    image = request.form.get('image')

    item = {
        'item_name': item_name,
        'category': category,
        'expiry': expiry,
        'rate': rate,
        'image': image
    }

    return render_template('order.html', item=item)

@app.route('/order_success', methods=['POST'])
def order_success():
    if 'username' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    item_name = request.form.get('item_name')
    category = request.form.get('category')
    expiry = request.form.get('expiry')
    rate = request.form.get('rate')
    image = request.form.get('image')
    address = request.form.get('address')

    print(f"Order placed by {session['username']} for {item_name} at address: {address}")

    return render_template('order_success.html',
                           item_name=item_name,
                           category=category,
                           expiry=expiry,
                           rate=rate,
                           image=image,
                           address=address)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
