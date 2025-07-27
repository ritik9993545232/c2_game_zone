from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c2_game_zone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with game progress
    game_progress = db.relationship('GameProgress', backref='user', lazy=True, cascade='all, delete-orphan')

class GameProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(100), nullable=False)
    progress_data = db.Column(db.Text)
    score = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    lives = db.Column(db.Integer, default=3)
    game_state = db.Column(db.Text)  # JSON string for complex game states
    last_played = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique combination of user and game
    __table_args__ = (db.UniqueConstraint('user_id', 'game_name', name='unique_user_game'),)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('home.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True, 'redirect': url_for('home')})
        else:
            return jsonify({'success': False, 'error': 'Invalid email or password'})
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return jsonify({'success': False, 'error': 'Username or email already exists'})
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=password_hash)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the user
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            
            return jsonify({'success': True, 'redirect': url_for('home')})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Failed to create account'})
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/save_progress', methods=['POST'])
def save_progress():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    data = request.get_json()
    game_name = data.get('game_name')
    progress_data = data.get('progress_data')
    score = data.get('score', 0)
    level = data.get('level', 1)
    lives = data.get('lives', 3)
    game_state = data.get('game_state', '{}')
    
    # Check if progress already exists
    progress = GameProgress.query.filter_by(
        user_id=session['user_id'], 
        game_name=game_name
    ).first()
    
    if progress:
        # Update existing progress
        progress.progress_data = progress_data
        progress.score = score
        progress.level = level
        progress.lives = lives
        progress.game_state = game_state
        progress.last_played = datetime.utcnow()
    else:
        # Create new progress
        progress = GameProgress(
            user_id=session['user_id'],
            game_name=game_name,
            progress_data=progress_data,
            score=score,
            level=level,
            lives=lives,
            game_state=game_state
        )
        db.session.add(progress)
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to save progress'})

@app.route('/get_progress/<game_name>')
def get_progress(game_name):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    progress = GameProgress.query.filter_by(
        user_id=session['user_id'], 
        game_name=game_name
    ).first()
    
    if progress:
        return jsonify({
            'success': True,
            'progress_data': progress.progress_data,
            'score': progress.score,
            'level': progress.level,
            'lives': progress.lives,
            'game_state': progress.game_state,
            'last_played': progress.last_played.isoformat()
        })
    else:
        return jsonify({'success': False, 'error': 'No progress found'})

@app.route('/user_profile')
def user_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    progress_list = GameProgress.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('profile.html', user=user, progress_list=progress_list)

# Admin routes
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Get statistics
    total_users = User.query.count()
    total_games_played = GameProgress.query.count()
    total_score = db.session.query(db.func.sum(GameProgress.score)).scalar() or 0
    
    # Get recent activities
    recent_progress = GameProgress.query.order_by(GameProgress.last_played.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         user=user,
                         total_users=total_users,
                         total_games_played=total_games_played,
                         total_score=total_score,
                         recent_progress=recent_progress,
                         recent_users=recent_users)

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    users = User.query.all()
    return render_template('admin/users.html', user=user, users=users)

@app.route('/admin/progress')
def admin_progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    progress_list = GameProgress.query.all()
    return render_template('admin/progress.html', user=user, progress_list=progress_list)

@app.route('/admin/create_admin', methods=['POST'])
def create_admin():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    current_user = User.query.get(session['user_id'])
    if not current_user or not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Admin privileges required'})
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Check if user already exists
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        return jsonify({'success': False, 'error': 'Username or email already exists'})
    
    # Create new admin user
    password_hash = generate_password_hash(password)
    new_admin = User(username=username, email=email, password_hash=password_hash, is_admin=True)
    
    try:
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to create admin user'})

# API endpoint to check if user is logged in
@app.route('/check_auth')
def check_auth():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return jsonify({
            'logged_in': True,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        })
    return jsonify({'logged_in': False})

def create_first_admin():
    """Create the first admin user if no admin exists."""
    with app.app_context():
        admin_exists = User.query.filter_by(is_admin=True).first()
        if not admin_exists:
            # Create default admin user
            admin_password = generate_password_hash('admin123')
            admin_user = User(
                username='admin',
                email='admin@c2gamezone.com',
                password_hash=admin_password,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Default admin user created!")
            print("Username: admin")
            print("Password: admin123")
            print("Please change these credentials after first login!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_first_admin()
    
    # Check if running on Render (production)
    if os.environ.get('RENDER'):
        # Production settings
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
    else:
        # Development settings
        app.run(debug=True, host='0.0.0.0', port=5000) 