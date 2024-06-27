from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    conn = get_db_connection()
    cur = conn.cursor()
    user = cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    conn.close()
    if user:
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True)
