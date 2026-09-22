"""
AI Health Assistant - Complete Application with Admin Routes
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import hashlib
import secrets
import re
import bleach
from datetime import datetime, timedelta
import os
from functools import wraps
import model
import chatbot

# ========== INITIALIZE FLASK APP ==========
app = Flask(__name__)

# ========== SECURITY CONFIGURATION ==========
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# ========== DATABASE CONNECTION ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
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
        cursor = db.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      email TEXT UNIQUE NOT NULL,
                      password TEXT NOT NULL,
                      user_type TEXT DEFAULT 'patient',
                      role TEXT DEFAULT 'patient',
                      specialization TEXT,
                      license_number TEXT,
                      is_active INTEGER DEFAULT 1,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      last_login TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS patient_records
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER NOT NULL,
                      symptoms TEXT,
                      prediction TEXT,
                      severity TEXT,
                      confidence REAL DEFAULT 0,
                      advice TEXT,
                      date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER NOT NULL,
                      message TEXT,
                      response TEXT,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS login_attempts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      email TEXT,
                      ip_address TEXT,
                      success INTEGER,
                      attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS doctor_patients
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      doctor_id INTEGER NOT NULL,
                      patient_id INTEGER NOT NULL,
                      assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS doctor_reviews
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      record_id INTEGER NOT NULL,
                      doctor_id INTEGER NOT NULL,
                      doctor_notes TEXT,
                      confirmed_diagnosis TEXT,
                      prescription TEXT,
                      follow_up_date TEXT,
                      reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS prescriptions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      patient_id INTEGER NOT NULL,
                      doctor_id INTEGER NOT NULL,
                      medication TEXT NOT NULL,
                      dosage TEXT,
                      instructions TEXT,
                      start_date TEXT,
                      end_date TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        db.commit()
        print("✅ Database initialized")
        
        # Create admin user
        create_admin_user()

def create_admin_user():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email='admin@healthcare.com'")
    if not cursor.fetchone():
        salt = secrets.token_hex(16)
        hashed_pw = hashlib.sha256(('admin123' + salt).encode()).hexdigest() + ":" + salt
        cursor.execute('''INSERT INTO users (name, email, password, user_type, role, is_active)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       ('System Administrator', 'admin@healthcare.com', hashed_pw, 'admin', 'admin', 1))
        db.commit()
        print("✅ Admin user created: admin@healthcare.com / admin123")

init_db()

# ========== HELPER FUNCTIONS ==========

def sanitize_input(text):
    if not text:
        return text
    allowed_tags = ['b', 'i', 'em', 'strong', 'p', 'br']
    return bleach.clean(text, tags=allowed_tags, strip=True)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, "Password is valid"

def hash_password(password):
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest() + ":" + salt

def verify_password(password, hashed):
    if not hashed or ":" not in hashed:
        return False
    hash_part, salt = hashed.split(":")
    return hash_part == hashlib.sha256((password + salt).encode()).hexdigest()

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
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== PUBLIC ROUTES ==========

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = sanitize_input(request.form.get("email", ""))
        password = request.form.get("password", "")
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, password, user_type, role, is_active FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        
        if user and verify_password(password, user['password']):
            if user['is_active'] == 0:
                return render_template("login.html", error="Account deactivated")
            
            session.permanent = True
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = email
            session['user_type'] = user['user_type']
            session['role'] = user['role']
            
            if user['user_type'] == 'admin' or user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['user_type'] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Invalid email or password")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = sanitize_input(request.form.get("name", ""))
        email = sanitize_input(request.form.get("email", ""))
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not name or len(name) < 2:
            return render_template("register.html", error="Name must be at least 2 characters")
        if not validate_email(email):
            return render_template("register.html", error="Invalid email format")
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return render_template("register.html", error=message)
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            return render_template("register.html", error="Email already registered")
        
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, user_type, role) VALUES (?, ?, ?, 'patient', 'patient')",
            (name, email, hashed_password)
        )
        db.commit()
        
        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        new_user = cursor.fetchone()
        
        session['user_id'] = new_user['id']
        session['user_name'] = name
        session['user_email'] = email
        session['user_type'] = 'patient'
        session['role'] = 'patient'
        
        return redirect(url_for('dashboard'))
    
    return render_template("register.html")

@app.route("/dashboard")
@login_required
def dashboard():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template("dashboard.html", name=session['user_name'])

# ========== ADMIN ROUTES ==========

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = sanitize_input(request.form.get("email", ""))
        password = request.form.get("password", "")
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, password, role, is_active FROM users WHERE email=? AND role='admin'", (email,))
        admin = cursor.fetchone()
        
        if admin and verify_password(password, admin['password']):
            session.permanent = True
            session['user_id'] = admin['id']
            session['user_name'] = admin['name']
            session['user_email'] = email
            session['user_type'] = 'admin'
            session['role'] = 'admin'
            
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template("admin_login.html", error="Invalid admin credentials")
    
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='patient'")
    total_patients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='doctor'")
    total_doctors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM patient_records")
    total_records = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_chats = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT name, email, user_type, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent_users = cursor.fetchall()
    
    return render_template("admin_dashboard.html",
                         name=session['user_name'],
                         total_patients=total_patients,
                         total_doctors=total_doctors,
                         total_records=total_records,
                         total_chats=total_chats,
                         recent_users=recent_users)

@app.route("/admin/patients")
@admin_required
def admin_patients():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email, created_at, is_active FROM users WHERE user_type='patient' ORDER BY created_at DESC")
    patients = cursor.fetchall()
    return render_template("admin_patients.html", patients=patients)

@app.route("/admin/doctors")
@admin_required
def admin_doctors():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email, specialization, created_at, is_active FROM users WHERE user_type='doctor' ORDER BY created_at DESC")
    doctors = cursor.fetchall()
    return render_template("admin_doctors.html", doctors=doctors)

# ========== DOCTOR ROUTES ==========

@app.route("/doctor/login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        email = sanitize_input(request.form.get("email", ""))
        password = request.form.get("password", "")
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, password, user_type FROM users WHERE email=? AND user_type='doctor'", (email,))
        doctor = cursor.fetchone()
        
        if doctor and verify_password(password, doctor['password']):
            session['user_id'] = doctor['id']
            session['user_name'] = doctor['name']
            session['user_type'] = 'doctor'
            return redirect(url_for('doctor_dashboard'))
        else:
            return render_template("doctor_login.html", error="Invalid credentials")
    
    return render_template("doctor_login.html")

@app.route("/doctor/dashboard")
def doctor_dashboard():
    if session.get('user_type') != 'doctor':
        return redirect(url_for('doctor_login'))
    return render_template("doctor_dashboard.html", name=session['user_name'])

@app.route("/symptom_checker")
@login_required
def symptom_checker():
    return render_template("symptom_checker.html")

@app.route("/predict", methods=["POST"])
@login_required
def predict():
    symptoms = request.form.get("symptoms", "")
    result = model.predict_disease(symptoms)
    return render_template("dashboard.html", prediction_result=result, name=session['user_name'])

@app.route("/chatbot")
@login_required
def chatbot_page():
    return render_template("chatbot.html")

@app.route("/api/chatbot", methods=["POST"])
@login_required
def chatbot_api():
    data = request.get_json()
    message = data.get("message", "")
    response = chatbot.get_response(message)
    return jsonify({"response": response})

@app.route("/api/analytics")
@login_required
def analytics():
    return jsonify({"data": []})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AI Health Assistant Starting...")
    print("=" * 60)
    print(f"🌐 Server: http://127.0.0.1:5000")
    print("=" * 60)
    print("🔐 PATIENT LOGIN: http://127.0.0.1:5000/login")
    print("👨‍⚕️ DOCTOR LOGIN: http://127.0.0.1:5000/doctor/login")
    print("👨‍💼 ADMIN LOGIN: http://127.0.0.1:5000/admin/login")
    print("   Email: admin@healthcare.com")
    print("   Password: admin123")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)

# ========== ADD MISSING HELPER FUNCTIONS IF NOT EXISTS ==========

def get_db():
    """Get database connection"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def verify_password(password, hashed):
    """Verify password against hash"""
    if not hashed or ":" not in hashed:
        return False
    hash_part, salt = hashed.split(":")
    return hash_part == hashlib.sha256((password + salt).encode()).hexdigest()

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return text
    allowed_tags = ['b', 'i', 'em', 'strong', 'p', 'br']
    return bleach.clean(text, tags=allowed_tags, strip=True)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    """Decorator to require doctor login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'doctor':
            return redirect(url_for('doctor_login'))
        return f(*args, **kwargs)
    return decorated_function



# ========== PASSWORD RESET ROUTES ==========

import secrets
from datetime import datetime, timedelta

@app.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("3 per hour")
def forgot_password():
    """Request password reset"""
    if request.method == "POST":
        email = sanitize_input(request.form.get("email", ""))
        
        if not email or not validate_email(email):
            return render_template("forgot_password.html", error="Please enter a valid email")
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id, name FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            expires = (datetime.now() + timedelta(hours=1)).isoformat()
            
            # Save token to database
            cursor.execute("""
                UPDATE users SET reset_token=?, reset_token_expires=? WHERE id=?
            """, (token, expires, user['id']))
            
            # Log request
            cursor.execute("""
                INSERT INTO password_reset_requests (user_id, email, token, ip_address)
                VALUES (?, ?, ?, ?)
            """, (user['id'], email, token, request.remote_addr))
            
            db.commit()
            
            # In production, send email here
            reset_link = url_for('reset_password', token=token, _external=True)
            print(f"\n📧 PASSWORD RESET LINK (for demo):")
            print(f"   {reset_link}\n")
            
            return render_template("forgot_password.html", 
                                 success="Password reset link sent! Check your email.",
                                 reset_link=reset_link)  # Remove reset_link in production
        else:
            # Don't reveal if email exists (security)
            return render_template("forgot_password.html", 
                                 success="If an account exists, a reset link has been sent.")
    
    return render_template("forgot_password.html")

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset password with token"""
    db = get_db()
    cursor = db.cursor()
    
    # Verify token
    cursor.execute("""
        SELECT id, name, email, reset_token_expires 
        FROM users 
        WHERE reset_token=?
    """, (token,))
    user = cursor.fetchone()
    
    if not user:
        return render_template("reset_password.html", 
                             error="Invalid or expired reset link")
    
    # Check expiry
    if user['reset_token_expires']:
        expires = datetime.fromisoformat(user['reset_token_expires'])
        if datetime.now() > expires:
            return render_template("reset_password.html", 
                                 error="Reset link has expired. Please request a new one.")
    
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if password != confirm_password:
            return render_template("reset_password.html", 
                                 error="Passwords do not match", token=token)
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return render_template("reset_password.html", 
                                 error=message, token=token)
        
        # Update password
        hashed_password = hash_password(password)
        cursor.execute("""
            UPDATE users SET password=?, reset_token=NULL, reset_token_expires=NULL 
            WHERE id=?
        """, (hashed_password, user['id']))
        
        # Mark reset request as used
        cursor.execute("UPDATE password_reset_requests SET used=1 WHERE token=?", (token,))
        
        db.commit()
        
        print(f"✅ Password reset successfully for: {user['email']}")
        
        return render_template("login.html", 
                             success="Password reset successful! Please login with your new password.")
    
    return render_template("reset_password.html", token=token)


# ========== ADMIN: CHANGE PASSWORD ==========

@app.route("/admin/change-password", methods=["GET", "POST"])
def admin_change_password():
    """Admin - Change own password"""
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT password FROM users WHERE id=?", (session['user_id'],))
        admin = cursor.fetchone()
        
        if not verify_password(current_password, admin['password']):
            return render_template("admin_change_password.html", 
                                 name=session['user_name'],
                                 error="Current password is incorrect")
        
        if new_password != confirm_password:
            return render_template("admin_change_password.html", 
                                 name=session['user_name'],
                                 error="New passwords do not match")
        
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return render_template("admin_change_password.html", 
                                 name=session['user_name'],
                                 error=message)
        
        # Update password
        hashed_password = hash_password(new_password)
        cursor.execute("UPDATE users SET password=?, updated_at=? WHERE id=?", 
                      (hashed_password, datetime.now().isoformat(), session['user_id']))
        db.commit()
        
        return render_template("admin_change_password.html", 
                             name=session['user_name'],
                             success="✅ Password changed successfully!")
    
    return render_template("admin_change_password.html", name=session['user_name'])

# ========== ADMIN: USER MANAGEMENT ==========

@app.route("/admin/users")
def admin_users():
    """Admin - View and manage all users"""
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    db = get_db()
    cursor = db.cursor()
    
    # Get all users with their details
    cursor.execute("""
        SELECT u.id, u.name, u.email, u.user_type, u.role, u.specialization,
               u.license_number, u.is_active, u.created_at, u.last_login,
               (SELECT COUNT(*) FROM patient_records WHERE user_id = u.id) as record_count,
               (SELECT COUNT(*) FROM chat_history WHERE user_id = u.id) as chat_count,
               (SELECT COUNT(*) FROM prescriptions WHERE doctor_id = u.id) as prescription_count
        FROM users u
        WHERE u.role != 'admin'
        ORDER BY u.created_at DESC
    """)
    users = cursor.fetchall()
    
    # Count statistics
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='patient'")
    total_patients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='doctor'")
    total_doctors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active=0")
    inactive_users = cursor.fetchone()[0]
    
    return render_template("admin_users.html",
                         name=session['user_name'],
                         users=users,
                         total_patients=total_patients,
                         total_doctors=total_doctors,
                         inactive_users=inactive_users)

@app.route("/api/admin/add-user", methods=["POST"])
def admin_add_user():
    """API - Add new user (patient or doctor)"""
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    name = sanitize_input(data.get('name', ''))
    email = sanitize_input(data.get('email', ''))
    password = data.get('password', 'password123')
    user_type = data.get('user_type', 'patient')
    specialization = sanitize_input(data.get('specialization', ''))
    license_number = sanitize_input(data.get('license_number', ''))
    
    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400
    
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if email exists
    cursor.execute("SELECT id FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        return jsonify({"error": "Email already registered"}), 400
    
    # Hash password
    hashed_password = hash_password(password)
    
    try:
        cursor.execute("""
            INSERT INTO users (name, email, password, user_type, role, specialization, license_number, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (name, email, hashed_password, user_type, user_type, 
              specialization, license_number, datetime.now().isoformat()))
        db.commit()
        
        print(f"✅ Admin created new {user_type}: {name} ({email})")
        
        return jsonify({
            "success": True,
            "message": f"{user_type.title()} created successfully",
            "user_id": cursor.lastrowid
        })
    except Exception as e:
        print(f"❌ Error adding user: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/remove-user", methods=["POST"])
def admin_remove_user():
    """API - Remove or deactivate user"""
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    user_id = data.get('user_id')
    permanent = data.get('permanent', False)
    
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Get user info
    cursor.execute("SELECT name, email FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Prevent deleting self
    if user_id == session['user_id']:
        return jsonify({"error": "Cannot delete your own account"}), 400
    
    try:
        if permanent:
            # Permanent delete - remove all traces
            cursor.execute("DELETE FROM doctor_patients WHERE doctor_id=? OR patient_id=?", (user_id, user_id))
            cursor.execute("DELETE FROM patient_records WHERE user_id=?", (user_id,))
            cursor.execute("DELETE FROM chat_history WHERE user_id=?", (user_id,))
            cursor.execute("DELETE FROM prescriptions WHERE doctor_id=? OR patient_id=?", (user_id, user_id))
            cursor.execute("DELETE FROM doctor_reviews WHERE doctor_id=?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            message = f"User {user['name']} permanently deleted"
        else:
            # Soft delete - just deactivate
            cursor.execute("UPDATE users SET is_active=0 WHERE id=?", (user_id,))
            message = f"User {user['name']} deactivated"
        
        db.commit()
        print(f"✅ {message}")
        
        return jsonify({"success": True, "message": message})
    except Exception as e:
        print(f"❌ Error removing user: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/activate-user", methods=["POST"])
def admin_activate_user():
    """API - Reactivate deactivated user"""
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET is_active=1 WHERE id=?", (user_id,))
    db.commit()
    
    cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    
    return jsonify({"success": True, "message": f"User {user['name']} activated"})

# ========== ADMIN: HEALTH RECORDS ==========

@app.route("/admin/health-records")
def admin_health_records():
    """Admin - View all health records"""
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    db = get_db()
    cursor = db.cursor()
    
    # Get filter parameters
    severity = request.args.get('severity', 'all')
    prediction = request.args.get('prediction', 'all')
    patient_id = request.args.get('patient_id', '')
    
    # Build query
    query = """
        SELECT pr.id, pr.user_id, u.name as patient_name, u.email as patient_email,
               pr.symptoms, pr.prediction, pr.severity, pr.confidence, pr.advice,
               datetime(pr.date, 'localtime') as formatted_date
        FROM patient_records pr
        JOIN users u ON pr.user_id = u.id
        WHERE 1=1
    """
    params = []
    
    if severity != 'all':
        query += " AND pr.severity=?"
        params.append(severity)
    
    if prediction != 'all':
        query += " AND pr.prediction=?"
        params.append(prediction)
    
    if patient_id:
        query += " AND pr.user_id=?"
        params.append(patient_id)
    
    query += " ORDER BY pr.date DESC LIMIT 500"
    
    cursor.execute(query, params)
    records = cursor.fetchall()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM patient_records")
    total_records = cursor.fetchone()[0]
    
    cursor.execute("SELECT severity, COUNT(*) FROM patient_records GROUP BY severity")
    severity_stats = dict(cursor.fetchall())
    
    cursor.execute("SELECT prediction, COUNT(*) FROM patient_records GROUP BY prediction ORDER BY COUNT(*) DESC LIMIT 10")
    prediction_stats = cursor.fetchall()
    
    # Get all patients for filter dropdown
    cursor.execute("SELECT id, name FROM users WHERE user_type='patient' ORDER BY name")
    patients = cursor.fetchall()
    
    return render_template("admin_health_records.html",
                         name=session['user_name'],
                         records=records,
                         total_records=total_records,
                         severity_stats=severity_stats,
                         prediction_stats=prediction_stats,
                         patients=patients,
                         current_severity=severity,
                         current_prediction=prediction,
                         current_patient=patient_id)

@app.route("/api/admin/health-record/<int:record_id>")
def admin_get_health_record(record_id):
    """API - Get single health record details"""
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT pr.*, u.name as patient_name, u.email as patient_email
        FROM patient_records pr
        JOIN users u ON pr.user_id = u.id
        WHERE pr.id=?
    """, (record_id,))
    record = cursor.fetchone()
    
    if not record:
        return jsonify({"error": "Record not found"}), 404
    
    return jsonify({
        "id": record['id'],
        "patient_name": record['patient_name'],
        "patient_email": record['patient_email'],
        "symptoms": record['symptoms'],
        "prediction": record['prediction'],
        "severity": record['severity'],
        "confidence": record['confidence'],
        "advice": record['advice'],
        "date": record['date']
    })

# ========== ADMIN: CHAT MESSAGES ==========

@app.route("/admin/chat-messages")
def admin_chat_messages():
    """Admin - View all chat messages"""
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    db = get_db()
    cursor = db.cursor()
    
    # Get filter
    user_filter = request.args.get('user_id', '')
    search = request.args.get('search', '')
    
    query = """
        SELECT ch.id, ch.user_id, u.name as user_name, u.email as user_email,
               ch.message, ch.response, datetime(ch.timestamp, 'localtime') as formatted_time
        FROM chat_history ch
        JOIN users u ON ch.user_id = u.id
        WHERE 1=1
    """
    params = []
    
    if user_filter:
        query += " AND ch.user_id=?"
        params.append(user_filter)
    
    if search:
        query += " AND (ch.message LIKE ? OR ch.response LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")
    
    query += " ORDER BY ch.timestamp DESC LIMIT 500"
    
    cursor.execute(query, params)
    messages = cursor.fetchall()
    
    # Statistics
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT u.name, COUNT(*) as count 
        FROM chat_history ch 
        JOIN users u ON ch.user_id = u.id 
        GROUP BY ch.user_id 
        ORDER BY count DESC 
        LIMIT 10
    """)
    top_users = cursor.fetchall()
    
    # Get all users for filter
    cursor.execute("SELECT id, name FROM users WHERE user_type='patient' ORDER BY name")
    users = cursor.fetchall()
    
    return render_template("admin_chat_messages.html",
                         name=session['user_name'],
                         messages=messages,
                         total_messages=total_messages,
                         top_users=top_users,
                         users=users,
                         current_user=user_filter,
                         search=search)

@app.route("/api/admin/chat-stats")
def admin_chat_stats():
    """API - Get chat statistics"""
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    db = get_db()
    cursor = db.cursor()
    
    # Messages per day (last 7 days)
    cursor.execute("""
        SELECT date(timestamp) as day, COUNT(*) as count
        FROM chat_history
        WHERE timestamp >= date('now', '-7 days')
        GROUP BY date(timestamp)
        ORDER BY day
    """)
    daily_stats = cursor.fetchall()
    
    return jsonify({
        "daily": [(row[0], row[1]) for row in daily_stats]
    })


# ========== ADMIN: CHANGE PASSWORD ==========

@app.route("/admin/dashboard")
def admin_dashboard_updated():
    """Admin dashboard with active page tracking"""
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    db = get_db()
    cursor = db.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='patient'")
    total_patients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='doctor'")
    total_doctors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM patient_records")
    total_records = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_chats = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM prescriptions")
    total_prescriptions = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM doctor_reviews")
    total_reviews = cursor.fetchone()[0]
    
    # Get recent users
    cursor.execute("""
        SELECT name, email, user_type, role, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent_users = cursor.fetchall()
    
    return render_template("admin_dashboard.html",
                         name=session['user_name'],
                         total_patients=total_patients,
                         total_doctors=total_doctors,
                         total_records=total_records,
                         total_chats=total_chats,
                         total_prescriptions=total_prescriptions,
                         total_reviews=total_reviews,
                         recent_users=recent_users,
                         active_page='dashboard')

@app.route("/admin/users")
def admin_users_updated():
    """Admin - View and manage all users"""
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT u.id, u.name, u.email, u.user_type, u.role, u.specialization,
               u.license_number, u.is_active, u.created_at, u.last_login,
               (SELECT COUNT(*) FROM patient_records WHERE user_id = u.id) as record_count,
               (SELECT COUNT(*) FROM chat_history WHERE user_id = u.id) as chat_count
        FROM users u
        WHERE u.role != 'admin'
        ORDER BY u.created_at DESC
    """)
    users = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='patient'")
    total_patients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='doctor'")
    total_doctors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active=0")
    inactive_users = cursor.fetchone()[0]
    
    return render_template("admin_users.html",
                         name=session['user_name'],
                         users=users,
                         total_patients=total_patients,
                         total_doctors=total_doctors,
                         inactive_users=inactive_users,
                         active_page='users')

@app.route("/admin/health-records")
def admin_health_records_updated():
    """Admin - View all health records"""
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    db = get_db()
    cursor = db.cursor()
    
    severity = request.args.get('severity', 'all')
    patient_id = request.args.get('patient_id', '')
    
    query = """
        SELECT pr.id, pr.user_id, u.name as patient_name, u.email as patient_email,
               pr.symptoms, pr.prediction, pr.severity, pr.confidence, pr.advice,
               datetime(pr.date, 'localtime') as formatted_date
        FROM patient_records pr
        JOIN users u ON pr.user_id = u.id
        WHERE 1=1
    """
    params = []
    
    if severity != 'all':
        query += " AND pr.severity=?"
        params.append(severity)
    
    if patient_id:
        query += " AND pr.user_id=?"
        params.append(patient_id)
    
    query += " ORDER BY pr.date DESC LIMIT 500"
    
    cursor.execute(query, params)
    records = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM patient_records")
    total_records = cursor.fetchone()[0]
    
    cursor.execute("SELECT severity, COUNT(*) FROM patient_records GROUP BY severity")
    severity_stats = dict(cursor.fetchall())
    
    cursor.execute("SELECT id, name FROM users WHERE user_type='patient' ORDER BY name")
    patients = cursor.fetchall()
    
    return render_template("admin_health_records.html",
                         name=session['user_name'],
                         records=records,
                         total_records=total_records,
                         severity_stats=severity_stats,
                         patients=patients,
                         current_severity=severity,
                         current_patient=patient_id,
                         active_page='records')

@app.route("/admin/chat-messages")
def admin_chat_messages_updated():
    """Admin - View all chat messages"""
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    db = get_db()
    cursor = db.cursor()
    
    user_filter = request.args.get('user_id', '')
    search = request.args.get('search', '')
    
    query = """
        SELECT ch.id, ch.user_id, u.name as user_name, u.email as user_email,
               ch.message, ch.response, datetime(ch.timestamp, 'localtime') as formatted_time
        FROM chat_history ch
        JOIN users u ON ch.user_id = u.id
        WHERE 1=1
    """
    params = []
    
    if user_filter:
        query += " AND ch.user_id=?"
        params.append(user_filter)
    
    if search:
        query += " AND (ch.message LIKE ? OR ch.response LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")
    
    query += " ORDER BY ch.timestamp DESC LIMIT 500"
    
    cursor.execute(query, params)
    messages = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT u.name, COUNT(*) as count 
        FROM chat_history ch 
        JOIN users u ON ch.user_id = u.id 
        GROUP BY ch.user_id 
        ORDER BY count DESC 
        LIMIT 10
    """)
    top_users = cursor.fetchall()
    
    cursor.execute("SELECT id, name FROM users WHERE user_type='patient' ORDER BY name")
    users = cursor.fetchall()
    
    return render_template("admin_chat_messages.html",
                         name=session['user_name'],
                         messages=messages,
                         total_messages=total_messages,
                         top_users=top_users,
                         users=users,
                         current_user=user_filter,
                         search=search,
                         active_page='chats')

@app.route("/admin/change-password", methods=["GET", "POST"])
def admin_change_password_updated():
    """Admin - Change own password"""
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT password FROM users WHERE id=?", (session['user_id'],))
        admin = cursor.fetchone()
        
        if not verify_password(current_password, admin['password']):
            return render_template("admin_change_password.html", 
                                 name=session['user_name'],
                                 error="Current password is incorrect",
                                 active_page='password')
        
        if new_password != confirm_password:
            return render_template("admin_change_password.html", 
                                 name=session['user_name'],
                                 error="New passwords do not match",
                                 active_page='password')
        
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return render_template("admin_change_password.html", 
                                 name=session['user_name'],
                                 error=message,
                                 active_page='password')
        
        hashed_password = hash_password(new_password)
        cursor.execute("UPDATE users SET password=? WHERE id=?", 
                      (hashed_password, session['user_id']))
        db.commit()
        
        return render_template("admin_change_password.html", 
                             name=session['user_name'],
                             success="✅ Password changed successfully!",
                             active_page='password')
    
    return render_template("admin_change_password.html", 
                         name=session['user_name'],
                         active_page='password')


# ========== ROUTE ALIASES FOR NEW ADMIN FUNCTIONS ==========
# These ensure the updated routes are used

# Override old routes with new function names
app.view_functions['admin_dashboard'] = admin_dashboard_updated
app.view_functions['admin_users'] = admin_users_updated
app.view_functions['admin_health_records'] = admin_health_records_updated
app.view_functions['admin_chat_messages'] = admin_chat_messages_updated
app.view_functions['admin_change_password'] = admin_change_password_updated

print("✅ Admin routes linked successfully")

