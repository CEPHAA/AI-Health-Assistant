from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import hashlib
import json
from datetime import datetime
import model
import chatbot

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Patient records table
    c.execute('''CREATE TABLE IF NOT EXISTS patient_records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  symptoms TEXT,
                  prediction TEXT,
                  severity TEXT,
                  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized/connected successfully")

# Call init_db to ensure tables exist
init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Invalid credentials")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                     (name, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Email already exists")
    
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get recent records
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(""" 
        SELECT symptoms, prediction, severity, 
               datetime(date, 'localtime') as formatted_date 
        FROM patient_records 
        WHERE user_id=? 
        ORDER BY date DESC 
        LIMIT 10
    """, (session['user_id'],))
    records = c.fetchall()
    conn.close()
    
    return render_template("dashboard.html", 
                         name=session['user_name'], 
                         records=records,
                         prediction_result=None)

@app.route("/symptom_checker")
def symptom_checker():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("symptom_checker.html")

@app.route("/predict", methods=["POST"])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    symptoms = request.form.get("symptoms", "")
    
    # Get prediction from model
    result = model.predict_disease(symptoms)
    
    # Save to database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO patient_records (user_id, symptoms, prediction, severity) VALUES (?, ?, ?, ?)",
              (session['user_id'], symptoms, result['disease'], result['severity']))
    conn.commit()
    conn.close()
    
    return render_template("dashboard.html", 
                         name=session['user_name'],
                         prediction_result=result,
                         symptoms=symptoms,
                         records=[])

@app.route("/chatbot")
def chatbot_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("chatbot.html")

@app.route("/api/chatbot", methods=["POST"])
def chatbot_api():
    data = request.json
    message = data.get("message", "")
    response = chatbot.get_response(message)
    return jsonify({"response": response})

@app.route("/api/analytics")
def analytics():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401  # ← Added proper indentation and fixed comma
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT prediction, COUNT(*) FROM patient_records WHERE user_id=?", (session['user_id'],))
    data = c.fetchall()
    conn.close()
    
    return jsonify({"data": data})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
