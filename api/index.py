from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'users.db'

# Initialize database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT UNIQUE NOT NULL,
                          password TEXT NOT NULL)''')
        conn.commit()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return render_template('register.html', error="Username already exists!")
    return render_template('register.html', error=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="Invalid credentials!")
    return render_template('login.html', error=None)

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        query = request.form['query']

        model_url = "https://api-inference.huggingface.co/models/facebook/llama-7b"
        headers = {"Authorization": "Bearer your-hugging-face-api-key"}
        payload = {"inputs": query}

        response = requests.post(model_url, headers=headers, json=payload)
        result = response.json()

        return render_template('ask.html', query=query, result=result.get('generated_text', 'No response'))
    return render_template('ask.html', query=None, result=None)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
