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
            background: linear-gradient(135deg, #fd297b 0%, #ff655b 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }

        .admin-container {
            background: #fff;
            border-radius: 15px;
            max-width: 1000px;
            margin: 0 auto;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }

        .logo { font-size: 40px; font-weight: 800; color: #fd297b; margin-bottom: 10px; text-align: center; }
        h2 { color: #333; margin-bottom: 10px; font-size: 20px; text-align: center; }
        .welcome-text { text-align: center; color: #666; margin-bottom: 30px; }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th { background-color: #f8f8f8; color: #666; font-weight: 600; }
        
        .password-cell { color: #aaa; font-family: monospace; letter-spacing: 2px;}

        .btn-danger {
            background: #ff4d4d;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s ease;
        }
        .btn-danger:hover { background: #e03333; }
        
        .logout-btn {
            display: inline-block;
            background: linear-gradient(135deg, #fd297b 0%, #ff655b 100%);
            color: white;
            text-decoration: none;
            padding: 12px 30px;
            border-radius: 30px;
            font-weight: 600;
            margin-top: 30px;
            text-align: center;
            transition: transform 0.2s ease;
        }
        .logout-btn:hover { transform: scale(1.02); }
        .flash {
            background: #d4edda;
            color: #155724;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
<div class="admin-container">
    <div class="logo">tinder</div>
    <h2>Admin Controls</h2>
    <div class="welcome-text">Welcome back, Administrator. Here are the registered users.</div>
    
    {% if flash_message %}
    <div class="flash">{{ flash_message }}</div>
    {% endif %}
    
    <div style="overflow-x: auto;">
        <table>
            <thead>
                <tr><th>ID</th><th>Username</th><th>Password</th><th>Role</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {% for u in users %}
                <tr>
                    <td>{{ u.id }}</td>
                    <td>{{ u.username }}</td>
                    <td class="password-cell">********</td>
                    <td>{{ 'Admin' if u.is_admin else 'Standard User' }}</td>
                    <td>
                        {% if not u.is_admin %}
                        <form method="POST" action="/delete/{{ u.id }}" style="margin:0;" onsubmit="return confirm('Delete this user?');">
                            <button type="submit" class="btn-danger">Delete</button>
                        </form>
                        {% else %}
                        —
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
</body>
</html>
