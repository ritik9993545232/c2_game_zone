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

# Initialize database function
def init_database():
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("Database tables created successfully")
            
            # Create admin user if none exists
            admin_exists = User.query.filter_by(is_admin=True).first()
            if not admin_exists:
                admin_password = generate_password_hash('admin123')
                admin_user = User(
                    username='admin',
                    email='admin@c2gamezone.com',
                    password_hash=admin_password,
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Default admin user created: admin@c2gamezone.com / admin123")
            else:
                print("Admin user already exists")
                
    except Exception as e:
        print(f"Database initialization error: {e}")
        print(traceback.format_exc())

# Routes
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        error_msg = f"Error loading index page: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg, 500

@app.route('/home')
def home():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))
        return render_template('home.html', user=user)
    except Exception as e:
        return f"Error loading home page: {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
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
        except Exception as e:
            return jsonify({'success': False, 'error': f'Login error: {str(e)}'})
    
    try:
        return render_template('login.html')
    except Exception as e:
        return f"Error loading login page: {str(e)}", 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # Ensure database is initialized
            init_database()
            
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
            
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Account created successfully! Please log in.'})
        except Exception as e:
            db.session.rollback()
            error_msg = f'Signup error: {str(e)}'
            print(error_msg)
            print(traceback.format_exc())
            return jsonify({'success': False, 'error': error_msg})
    
    try:
        return render_template('signup.html')
    except Exception as e:
        return f"Error loading signup page: {str(e)}", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/save_progress', methods=['POST'])
def save_progress():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'User not logged in'})
        
        data = request.get_json()
        user_id = session['user_id']
        game_name = data.get('game_name')
        progress_data = data.get('progress_data', '{}')
        score = data.get('score', 0)
        level = data.get('level', 1)
        lives = data.get('lives', 3)
        game_state = data.get('game_state', '{}')
        
        # Check if progress already exists
        existing_progress = GameProgress.query.filter_by(
            user_id=user_id, 
            game_name=game_name
        ).first()
        
        if existing_progress:
            # Update existing progress
            existing_progress.progress_data = progress_data
            existing_progress.score = score
            existing_progress.level = level
            existing_progress.lives = lives
            existing_progress.game_state = game_state
            existing_progress.last_played = datetime.utcnow()
        else:
            # Create new progress
            new_progress = GameProgress(
                user_id=user_id,
                game_name=game_name,
                progress_data=progress_data,
                score=score,
                level=level,
                lives=lives,
                game_state=game_state
            )
            db.session.add(new_progress)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_progress/<game_name>')
def get_progress(game_name):
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'User not logged in'})
        
        user_id = session['user_id']
        progress = GameProgress.query.filter_by(
            user_id=user_id, 
            game_name=game_name
        ).first()
        
        if progress:
            return jsonify({
                'success': True,
                'score': progress.score,
                'level': progress.level,
                'lives': progress.lives,
                'game_state': progress.game_state,
                'progress_data': progress.progress_data
            })
        else:
            return jsonify({
                'success': True,
                'score': 0,
                'level': 1,
                'lives': 3,
                'game_state': '{}',
                'progress_data': '{}'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/user_profile')
def user_profile():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))
        
        # Get user's game progress
        progress_list = GameProgress.query.filter_by(user_id=user.id).all()
        
        # Calculate statistics
        total_games = len(progress_list)
        total_score = sum(p.score for p in progress_list)
        highest_score = max([p.score for p in progress_list] + [0])
        
        return render_template('profile.html', 
                             user=user, 
                             progress_list=progress_list,
                             total_games=total_games,
                             total_score=total_score,
                             highest_score=highest_score)
    except Exception as e:
        return f"Error loading profile: {str(e)}", 500

# Admin routes
@app.route('/admin')
def admin_dashboard():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return redirect(url_for('home'))
        
        # Get statistics
        total_users = User.query.count()
        total_games_played = GameProgress.query.count()
        total_score = db.session.query(db.func.sum(GameProgress.score)).scalar() or 0
        
        # Get recent activity
        recent_progress = GameProgress.query.order_by(GameProgress.last_played.desc()).limit(10).all()
        recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
        
        return render_template('admin/dashboard.html', 
                             user=user,
                             total_users=total_users,
                             total_games_played=total_games_played,
                             total_score=total_score,
                             recent_progress=recent_progress,
                             recent_users=recent_users)
    except Exception as e:
        return f"Error loading admin dashboard: {str(e)}", 500

@app.route('/admin/users')
def admin_users():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return redirect(url_for('home'))
        
        users = User.query.all()
        return render_template('admin/users.html', user=user, users=users)
    except Exception as e:
        return f"Error loading admin users: {str(e)}", 500

@app.route('/admin/progress')
def admin_progress():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return redirect(url_for('home'))
        
        progress_list = GameProgress.query.all()
        return render_template('admin/progress.html', user=user, progress_list=progress_list)
    except Exception as e:
        return f"Error loading admin progress: {str(e)}", 500

@app.route('/admin/create_admin', methods=['POST'])
def create_admin():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'})
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'success': False, 'error': 'Not authorized'})
        
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            existing_user.is_admin = True
            db.session.commit()
            return jsonify({'success': True, 'message': f'User {username} is now an admin'})
        
        # Create new admin user
        password_hash = generate_password_hash(password)
        new_admin = User(username=username, email=email, password_hash=password_hash, is_admin=True)
        
        db.session.add(new_admin)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Admin user {username} created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/check_auth')
def check_auth():
    try:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                return jsonify({'authenticated': True, 'username': user.username, 'is_admin': user.is_admin})
        return jsonify({'authenticated': False})
    except Exception as e:
        return jsonify({'authenticated': False, 'error': str(e)})

@app.route('/init_db')
def init_db_route():
    try:
        init_database()
        return jsonify({'success': True, 'message': 'Database initialized successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Production settings for Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
