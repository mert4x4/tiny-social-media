from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import secrets
import os
from dotenv import load_dotenv

load_dotenv()

key = secrets.token_hex(32)

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'db')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'user')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'password')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DATABASE', 'social_media')
app.secret_key = key

mysql = MySQL(app)
bcrypt = Bcrypt(app)

def check_db_connection():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT DATABASE();")
            db_name = cur.fetchone()
            print(f"Connected to the database: {db_name[0]}")
            cur.close()
        except Exception as e:
            print(f"Error connecting to the database: {str(e)}")

check_db_connection()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
    except Exception as e:
        print(f"Error registering user {username}: {e}")
        return "An error occurred during registration", 500
    finally:
        cur.close()

    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()

    if user and bcrypt.check_password_hash(user[2], password):
        session['username'] = username
        return redirect(url_for('feed'))
    else:
        return "Invalid username or password", 401

@app.route('/feed', methods=['GET'])
def feed():
    username = session.get('username')
    return render_template('feed.html', username=username)

@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'POST':
        username = session.get('username')
        if not username:
            return jsonify({"error": "User not logged in"}), 401

        content = request.json.get('content')
        if not content:
            return jsonify({"error": "No content provided"}), 400

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO posts (username, content) VALUES (%s, %s)", (username, content))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Post added!"}), 201

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, content, username, created_at FROM posts")
    posts = cur.fetchall()
    cur.close()

    return jsonify({
        "posts": [
            {
                "id": post[0],
                "content": post[1],
                "username": post[2],
                "created_at": post[3].strftime("%Y-%m-%d %H:%M:%S")
            }
            for post in posts
        ]
    })

@app.route('/api/comments/<int:post_id>', methods=['GET', 'POST'])
def handle_comments(post_id):
    if request.method == 'POST':
        username = session.get('username')
        if not username:
            return jsonify({"error": "User not logged in"}), 401

        content = request.json.get('content')
        if not content:
            return jsonify({"error": "No content provided"}), 400

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO comments (post_id, username, content) VALUES (%s, %s, %s)", (post_id, username, content))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Comment added!"}), 201

    cur = mysql.connection.cursor()
    cur.execute("SELECT content, username, created_at FROM comments WHERE post_id = %s", (post_id,))
    comments = cur.fetchall()
    cur.close()

    return jsonify({
        "comments": [
            {
                "content": comment[0],
                "username": comment[1],
                "created_at": comment[2].strftime("%Y-%m-%d %H:%M:%S")
            }
            for comment in comments
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('WEB_PORT', 8080)))