import os
import sqlite3
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session, flash, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# --- App Configuration ---
# Point Flask to the templates folder one level up in the root directory
basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(basedir, '../templates')

app = Flask(__name__, template_folder=template_dir)

# Pull secret key from environment variables to secure session data
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'super_secret_development_key')
DATABASE = 'users.db'

# --- Database Management ---
def get_db():
   db = getattr(g, '_database', None)
   if db is None:
       db = g._database = sqlite3.connect(DATABASE)
       db.row_factory = sqlite3.Row
   return db

@app.teardown_appcontext
def close_connection(exception):
   db = getattr(g, '_database', None)
   if db is not None:
       db.close()

def init_db():
   with app.app_context():
       db = get_db()
       db.execute('''
           CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT UNIQUE NOT NULL,
               password TEXT NOT NULL,
               is_admin INTEGER DEFAULT 0
           )
       ''')
       admin = db.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
       if not admin:
           # Secure the default admin account with a hashed password
           hashed_admin_pass = generate_password_hash('adminpass')
           db.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                      ('admin', hashed_admin_pass, 1))
       db.commit()

# --- Auth Decorators ---
def login_required(f):
   @wraps(f)
   def decorated_function(*args, **kwargs):
       if 'user_id' not in session:
           return redirect(url_for('login'))
       return f(*args, **kwargs)
   return decorated_function

def admin_required(f):
   @wraps(f)
   def decorated_function(*args, **kwargs):
       if 'user_id' not in session or not session.get('is_admin'):
           flash("Administrator access required.")
           return redirect(url_for('dashboard'))
       return f(*args, **kwargs)
   return decorated_function

# --- Routes ---
@app.route('/')
def login():
   if 'user_id' in session:
       return redirect(url_for('admin') if session.get('is_admin') else url_for('dashboard'))
   return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
   data = request.get_json()
   username = data.get('username', '')
   password = data.get('password', '')
   
   user = get_db().execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
   
   # Safely verify the hashed password instead of checking plaintext
   if user and check_password_hash(user['password'], password):
       session['user_id'] = user['id']
       session['username'] = user['username']
       session['is_admin'] = bool(user['is_admin'])
       return jsonify({'success': True, 'redirect': url_for('admin') if user['is_admin'] else url_for('dashboard')})
   return jsonify({'success': False, 'error': 'Invalid credentials.'})

@app.route('/register')
def register_page():
   if 'user_id' in session:
       return redirect(url_for('dashboard'))
   return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
   data = request.get_json()
   username = data.get('username', '').strip()
   password = data.get('password', '')
   
   if not username or not password:
       return jsonify({'success': False, 'error': 'Username and password required.'})
   
   db = get_db()
   existing = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
   if existing:
       return jsonify({'success': False, 'error': 'Username already exists.'})
   
   # Hash the user's password before committing to the database
   hashed_password = generate_password_hash(password)
   db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
   db.commit()
   return jsonify({'success': True, 'redirect': url_for('login')})

@app.route('/dashboard')
@login_required
def dashboard():
   if session.get('is_admin'):
       return redirect(url_for('admin'))
   return render_template('user_dashboard.html', username=session['username'])

@app.route('/admin')
@admin_required
def admin():
   users = get_db().execute('SELECT id, username, password, is_admin FROM users').fetchall()
   flash_message = request.args.get('flash', None)
   return render_template('admin_dashboard.html', users=users, flash_message=flash_message)

@app.route('/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
   db = get_db()
   if user_id != session['user_id']:
       db.execute('DELETE FROM users WHERE id = ?', (user_id,))
       db.commit()
       return redirect(url_for('admin', flash='User successfully deleted.'))
   return redirect(url_for('admin', flash='Cannot delete your own account.'))

@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for('login'))

if __name__ == '__main__':
   init_db() 
   app.run(debug=True, port=5000)
