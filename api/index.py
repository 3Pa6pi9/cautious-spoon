import sqlite3
from functools import wraps
from flask import Flask, request, render_template_string, redirect, url_for, session, flash, g, jsonify

app = Flask(__name__)
app.secret_key = 'super_secret_development_key'
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
           db.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                      ('admin', 'adminpass', 1))
       db.commit()

# --- Login Page HTML (Tinder Aesthetic) ---
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>Log in to Tinder</title>
   <style>
       * { box-sizing: border-box; }
       body {
           margin: 0;
           font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
           background: linear-gradient(135deg, #fd297b 0%, #ff655b 100%);
           height: 100vh;
           display: flex;
           justify-content: center;
           align-items: center;
       }

       .login-modal {
           background: #fff;
           padding: 40px;
           border-radius: 15px;
           width: 90%;
           max-width: 380px;
           text-align: center;
           box-shadow: 0 20px 40px rgba(0,0,0,0.2);
           transform: scale(1);
           transition: transform 0.3s ease, opacity 0.5s ease;
       }

       .logo { font-size: 50px; font-weight: 800; color: #fd297b; margin-bottom: 20px; }
       h2 { color: #333; margin-bottom: 30px; font-size: 20px; }

       .input-field {
           display: block;
           width: 100%;
           padding: 14px 20px;
           margin: 12px 0;
           border: 2px solid #ddd;
           border-radius: 30px;
           font-size: 14px;
           color: #333;
           outline: none;
           transition: border-color 0.2s ease;
       }

       .input-field:focus {
           border-color: #fd297b;
       }

       .input-field::placeholder {
           color: #aaa;
           font-weight: 500;
       }

       .btn {
           display: block;
           width: 100%;
           padding: 14px;
           margin: 12px 0;
           border: 2px solid #ddd;
           border-radius: 30px;
           text-decoration: none;
           color: #444;
           font-weight: 600;
           font-size: 14px;
           background: #fff;
           cursor: pointer;
           transition: all 0.2s ease;
           outline: none;
       }

       .btn:active { transform: scale(0.98); }

       .submit-btn {
           background: linear-gradient(135deg, #fd297b 0%, #ff655b 100%);
           color: #fff;
           border: none;
           margin-top: 20px;
           box-shadow: 0 4px 15px rgba(253, 41, 123, 0.3);
       }

       .submit-btn:hover { 
           background: linear-gradient(135deg, #e0246b 0%, #ff5247 100%); 
       }

       .error-message {
           color: #ff3344;
           font-size: 13px;
           margin-top: 10px;
           margin-bottom: 5px;
           font-weight: 600;
       }

       .nav-link {
           margin-top: 20px;
           font-size: 13px;
       }
       .nav-link a {
           color: #fd297b;
           text-decoration: none;
           font-weight: 600;
       }
       .nav-link a:hover {
           text-decoration: underline;
       }

       .terms {
           font-size: 11px;
           color: #888;
           margin-top: 25px;
           padding: 0 10px;
           line-height: 1.4;
       }
   </style>
</head>
<body>

<div class="login-modal" id="loginCard">
   <div class="logo">tinder</div>
   <h2>Welcome Back</h2>
   
   <div id="errorMsg" class="error-message"></div>
   
   <form id="loginForm">
       <input type="text" id="username" class="input-field" placeholder="Email or Username" required>
       <input type="password" id="password" class="input-field" placeholder="Password" required>
       
       <button type="submit" class="btn submit-btn">LOG IN</button>
   </form>
   
   <div class="nav-link">
       <a href="/register">Don't have an account? Register here</a>
   </div>
   
   <p class="terms">
       By clicking Log In, you agree with our Terms. Learn how we process your data in our Privacy Policy and Cookies Policy.
   </p>
</div>

<script>
   const card = document.getElementById('loginCard');
   
   card.style.opacity = '0';
   setTimeout(() => { card.style.opacity = '1'; }, 100);
   
   document.getElementById('loginForm').addEventListener('submit', async function(event) {
       event.preventDefault();
       
       const username = document.getElementById('username').value.trim();
       const password = document.getElementById('password').value;
       const errorDiv = document.getElementById('errorMsg');
       
       card.style.transform = 'scale(0.95)';
       errorDiv.textContent = '';
       
       try {
           const response = await fetch('/api/login', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ username: username, password: password })
           });
           
           const data = await response.json();
           
           setTimeout(() => {
               card.style.transform = 'scale(1)';
               
               if (data.success) {
                   window.location.href = data.redirect;
               } else {
                   errorDiv.textContent = data.error || 'Invalid credentials.';
               }
           }, 150);
       } catch (err) {
           setTimeout(() => {
               card.style.transform = 'scale(1)';
               errorDiv.textContent = 'Network error. Please try again.';
           }, 150);
       }
   });
</script>

</body>
</html>
"""

# --- Register Page HTML (Tinder Aesthetic) ---
REGISTER_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>Create Account - Tinder</title>
   <style>
       * { box-sizing: border-box; }
       body {
           margin: 0;
           font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
           background: linear-gradient(135deg, #fd297b 0%, #ff655b 100%);
           height: 100vh;
           display: flex;
           justify-content: center;
           align-items: center;
       }

       .login-modal {
           background: #fff;
           padding: 40px;
           border-radius: 15px;
           width: 90%;
           max-width: 380px;
           text-align: center;
           box-shadow: 0 20px 40px rgba(0,0,0,0.2);
           transition: opacity 0.5s ease;
       }

       .logo { font-size: 50px; font-weight: 800; color: #fd297b; margin-bottom: 20px; }
       h2 { color: #333; margin-bottom: 30px; font-size: 20px; }

       .input-field {
           display: block;
           width: 100%;
           padding: 14px 20px;
           margin: 12px 0;
           border: 2px solid #ddd;
           border-radius: 30px;
           font-size: 14px;
           color: #333;
           outline: none;
           transition: border-color 0.2s ease;
       }

       .input-field:focus {
           border-color: #fd297b;
       }

       .btn {
           display: block;
           width: 100%;
           padding: 14px;
           margin: 12px 0;
           border: 2px solid #ddd;
           border-radius: 30px;
           text-decoration: none;
           color: #444;
           font-weight: 600;
           font-size: 14px;
           background: #fff;
           cursor: pointer;
           transition: all 0.2s ease;
       }

       .submit-btn {
           background: linear-gradient(135deg, #fd297b 0%, #ff655b 100%);
           color: #fff;
           border: none;
           margin-top: 20px;
           box-shadow: 0 4px 15px rgba(253, 41, 123, 0.3);
       }

       .submit-btn:hover { 
           background: linear-gradient(135deg, #e0246b 0%, #ff5247 100%); 
       }

       .error-message {
           color: #ff3344;
           font-size: 13px;
           margin-top: 10px;
           margin-bottom: 5px;
           font-weight: 600;
       }

       .nav-link {
           margin-top: 20px;
           font-size: 13px;
       }
       .nav-link a {
           color: #fd297b;
           text-decoration: none;
           font-weight: 600;
       }
   </style>
</head>
<body>

<div class="login-modal" id="registerCard">
   <div class="logo">tinder</div>
   <h2>Create Account</h2>
   
   <div id="errorMsg" class="error-message"></div>
   
   <form id="registerForm">
       <input type="text" id="username" class="input-field" placeholder="Choose a Username" required>
       <input type="password" id="password" class="input-field" placeholder="Choose a Password" required>
       
       <button type="submit" class="btn submit-btn">REGISTER</button>
   </form>
   
   <div class="nav-link">
       <a href="/">Already have an account? Log in</a>
   </div>
</div>

<script>
   const card = document.getElementById('registerCard');
   card.style.opacity = '0';
   setTimeout(() => { card.style.opacity = '1'; }, 100);
   
   document.getElementById('registerForm').addEventListener('submit', async function(event) {
       event.preventDefault();
       
       const username = document.getElementById('username').value.trim();
       const password = document.getElementById('password').value;
       const errorDiv = document.getElementById('errorMsg');
       
       errorDiv.textContent = '';
       
       try {
           const response = await fetch('/api/register', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ username: username, password: password })
           });
           
           const data = await response.json();
           
           if (data.success) {
               window.location.href = data.redirect;
           } else {
               errorDiv.textContent = data.error || 'Registration failed.';
           }
       } catch (err) {
           errorDiv.textContent = 'Network error. Please try again.';
       }
   });
</script>

</body>
</html>
"""

# --- Admin Dashboard Page (Tinder Dark Mode Aesthetic with CSV Export) ---
ADMIN_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>Admin Dashboard - Tinder</title>
   <style>
       * { box-sizing: border-box; }
       body {
           margin: 0;
           font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
           background: #111418;
           min-height: 100vh;
           padding: 40px 20px;
           color: #e1e3e6;
       }

       .admin-container {
           background: #21262d;
           border-radius: 15px;
           max-width: 1000px;
           margin: 0 auto;
           padding: 30px;
           box-shadow: 0 20px 40px rgba(0,0,0,0.6);
           border: 1px solid #30363d;
       }

       .logo { 
           font-size: 40px; 
           font-weight: 800; 
           margin-bottom: 10px; 
           text-align: center; 
           background: linear-gradient(135deg, #fd297b 0%, #ff655b 100%);
           -webkit-background-clip: text;
           -webkit-text-fill-color: transparent;
       }
       
       h2 { color: #ffffff; margin-bottom: 10px; font-size: 22px; text-align: center; }
       .welcome-text { color: #8b949e; margin: 0; }

       .header-controls {
           display: flex;
           justify-content: space-between;
           align-items: center;
           margin-bottom: 25px;
           margin-top: 30px;
           padding-bottom: 15px;
           border-bottom: 1px solid #30363d;
       }

       .export-btn {
           background: transparent;
           color: #ff655b;
           border: 2px solid #ff655b;
           padding: 8px 20px;
           border-radius: 20px;
           cursor: pointer;
           font-size: 13px;
           font-weight: 600;
           transition: all 0.2s ease;
       }
       
       .export-btn:hover {
           background: rgba(255, 101, 91, 0.1);
           transform: scale(1.02);
       }

       table {
           width: 100%;
           border-collapse: collapse;
           font-size: 14px;
       }
       th, td {
           padding: 14px 12px;
           text-align: left;
           border-bottom: 1px solid #30363d;
       }
       th {
           background-color: #161b22;
           color: #8b949e;
           font-weight: 600;
           text-transform: uppercase;
           font-size: 12px;
           letter-spacing: 0.5px;
       }
       tr:hover td {
           background-color: rgba(255,255,255,0.02);
       }
       .password-cell {
           color: #ff655b;
           font-family: monospace;
           letter-spacing: 1px;
       }
       .btn-danger {
           background: transparent;
           color: #ff4d4d;
           border: 1px solid #ff4d4d;
           padding: 6px 14px;
           border-radius: 20px;
           cursor: pointer;
           font-size: 12px;
           transition: background 0.2s ease;
       }
       .btn-danger:hover {
           background: rgba(255, 77, 77, 0.15);
       }
       .logout-btn {
           display: inline-block;
           background: linear-gradient(135deg, #fd297b 0%, #ff655b 100%);
           color: white;
           text-decoration: none;
           padding: 12px 35px;
           border-radius: 30px;
           font-weight: 600;
           margin-top: 40px;
           text-align: center;
           transition: transform 0.2s ease;
           box-shadow: 0 4px 15px rgba(253, 41, 123, 0.2);
       }
       .logout-btn:hover {
           transform: scale(1.03);
           box-shadow: 0 6px 20px rgba(253, 41, 123, 0.3);
       }
       .flash {
           background: rgba(46, 160, 67, 0.15);
           color: #3fb950;
           border: 1px solid rgba(46, 160, 67, 0.4);
           padding: 12px;
           border-radius: 10px;
           margin-bottom: 20px;
           text-align: center;
           font-weight: 500;
       }
   </style>
</head>
<body>
<div class="admin-container">
   <div class="logo">tinder</div>
   <h2>Admin Controls</h2>
   
   {% if flash_message %}
   <div class="flash">{{ flash_message }}</div>
   {% endif %}

   <div class="header-controls">
       <div class="welcome-text">Welcome back, Administrator.</div>
       <button onclick="exportTableToCSV('tinder_users.csv')" class="export-btn">Export Data (CSV)</button>
   </div>
   
   <div style="overflow-x: auto;">
       <table>
           <thead>
               <tr>
                   <th>ID</th>
                   <th>Username</th>
                   <th>Password</th>
                   <th>Role</th>
                   <th>Actions</th>
               </tr>
           </thead>
           <tbody>
               {% for u in users %}
               <tr>
                   <td>{{ u.id }}</td>
                   <td style="font-weight: 600;">{{ u.username }}</td>
                   <td class="password-cell">{{ u.password }}</td>
                   <td>
                       <span style="background: {{ 'rgba(253, 41, 123, 0.15); color: #fd297b;' if u.is_admin else 'rgba(139, 148, 158, 0.15); color: #8b949e;' }} padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">
                           {{ 'ADMIN' if u.is_admin else 'USER' }}
                       </span>
                   </td>
                   <td>
                       {% if not u.is_admin %}
                       <form method="POST" action="/delete/{{ u.id }}" style="margin:0;" onsubmit="return confirm('Delete this user permanently?');">
                           <button type="submit" class="btn-danger">Delete</button>
                       </form>
                       {% else %}
                       <span style="color: #555; font-size: 12px;">Protected</span>
                       {% endif %}
                   </td>
               </tr>
               {% endfor %}
           </tbody>
       </table>
   </div>
   <div style="text-align: center;">
       <a href="/logout" class="logout-btn">Log Out</a>
   </div>
</div>

<script>
   function exportTableToCSV(filename) {
       let csv = [];
       let rows = document.querySelectorAll("table tr");
       
       for (let i = 0; i < rows.length; i++) {
           let row = [];
           let cols = rows[i].querySelectorAll("td, th");
           
           for (let j = 0; j < cols.length - 1; j++) {
               let data = cols[j].innerText.replace(/"/g, '""');
               row.push('"' + data + '"');
           }
           csv.push(row.join(","));
       }

       let csvFile = new Blob([csv.join("\\n")], {type: "text/csv"});
       let downloadLink = document.createElement("a");
       downloadLink.download = filename;
       downloadLink.href = window.URL.createObjectURL(csvFile);
       downloadLink.style.display = "none";
       
       document.body.appendChild(downloadLink);
       downloadLink.click();
       document.body.removeChild(downloadLink);
   }
</script>
</body>
</html>
"""

# --- User Dashboard Page ---
USER_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>Dashboard - Tinder</title>
   <style>
       * { box-sizing: border-box; }
       body {
           margin: 0;
           font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
           background: linear-gradient(135deg, #fd297b 0%, #ff655b 100%);
           min-height: 100vh;
           display: flex;
           justify-content: center;
           align-items: center;
           padding: 20px;
       }

       .dashboard-card {
           background: #fff;
           border-radius: 15px;
           padding: 50px 40px;
           width: 100%;
           max-width: 500px;
           text-align: center;
           box-shadow: 0 20px 40px rgba(0,0,0,0.2);
       }

       .logo { font-size: 50px; font-weight: 800; color: #fd297b; margin-bottom: 20px; }
       h2 { color: #333; margin-bottom: 15px; }
       .welcome-message { color: #666; margin-bottom: 30px; font-size: 16px; }
       .logout-btn {
           display: inline-block;
           background: linear-gradient(135deg, #fd297b 0%, #ff655b 100%);
           color: white;
           text-decoration: none;
           padding: 12px 30px;
           border-radius: 30px;
           font-weight: 600;
           transition: transform 0.2s ease;
       }
       .logout-btn:hover {
           transform: scale(1.02);
       }
   </style>
</head>
<body>
<div class="dashboard-card">
   <div class="logo">tinder</div>
   <h2>Welcome back!</h2>
   <div class="welcome-message">You are logged in as <strong>{{ username }}</strong>.</div>
   <p style="color: #888; margin-bottom: 30px;">This is your standard dashboard. You don't have administrative privileges.</p>
   <a href="/logout" class="logout-btn">Log Out</a>
</div>
</body>
</html>
"""

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
   return render_template_string(LOGIN_PAGE)

@app.route('/api/login', methods=['POST'])
def api_login():
   data = request.get_json()
   username = data.get('username', '')
   password = data.get('password', '')
   
   user = get_db().execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
   
   if user and user['password'] == password:
       session['user_id'] = user['id']
       session['username'] = user['username']
       session['is_admin'] = bool(user['is_admin'])
       return jsonify({'success': True, 'redirect': url_for('admin') if user['is_admin'] else url_for('dashboard')})
   return jsonify({'success': False, 'error': 'Invalid credentials.'})

@app.route('/register')
def register_page():
   if 'user_id' in session:
       return redirect(url_for('dashboard'))
   return render_template_string(REGISTER_PAGE)

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
   
   db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
   db.commit()
   return jsonify({'success': True, 'redirect': url_for('login')})

@app.route('/dashboard')
@login_required
def dashboard():
   if session.get('is_admin'):
       return redirect(url_for('admin'))
   return render_template_string(USER_DASHBOARD, username=session['username'])

@app.route('/admin')
@admin_required
def admin():
   users = get_db().execute('SELECT id, username, password, is_admin FROM users').fetchall()
   flash_message = request.args.get('flash', None)
   return render_template_string(ADMIN_DASHBOARD, users=users, flash_message=flash_message)

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