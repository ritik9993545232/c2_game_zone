from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import secrets
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Database configuration for production
try:
    if os.environ.get('RENDER'):
        # Production: Use absolute path for Render
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/c2_game_zone.db'
    else:
        # Development: Use relative path
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c2_game_zone.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    print("Database configuration set successfully")
except Exception as e:
    print(f"Database configuration error: {e}")

try:
    db = SQLAlchemy(app)
    print("SQLAlchemy initialized successfully")
except Exception as e:
    print(f"SQLAlchemy initialization error: {e}")

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GameProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(100), nullable=False)
    progress_data = db.Column(db.Text)
    score = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    lives = db.Column(db.Integer, default=3)
    game_state = db.Column(db.Text)
    last_played = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Routes
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        error_msg = f"Error loading index page: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg, 500

@app.route('/test')
def test():
    return "Debug app is working!"

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
    except Exception as e:
        print(f"Database creation error: {e}")
        print(traceback.format_exc())
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 