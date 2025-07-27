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
            db.create_all()
            print("✅ Database tables created successfully")
            
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
                print("✅ Default admin user created: admin@c2gamezone.com / admin123")
            else:
                print("ℹ️ Admin user already exists")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print(traceback.format_exc())

# Routes
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        # Return simple HTML if template is missing
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>C2 Game Zone</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                }
                .logo { 
                    font-size: 48px; 
                    margin-bottom: 20px; 
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                .subtitle { 
                    font-size: 24px; 
                    margin-bottom: 40px; 
                    opacity: 0.9;
                }
                .btn { 
                    display: inline-block; 
                    padding: 15px 30px; 
                    margin: 10px; 
                    background: rgba(255,255,255,0.2); 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 25px;
                    border: 2px solid rgba(255,255,255,0.3);
                    transition: all 0.3s ease;
                }
                .btn:hover {
                    background: rgba(255,255,255,0.3);
                    transform: translateY(-2px);
                }
                .status {
                    margin-top: 30px;
                    font-size: 14px;
                    opacity: 0.7;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🎮 C2 Game Zone</div>
                <div class="subtitle">Your Gaming Hub</div>
                <a href="/login" class="btn">Sign In</a>
                <a href="/signup" class="btn">Create Account</a>
                <div class="status">
                    <p>✅ Server is running!</p>
                    <p><a href="/test" style="color: white;">Test Route</a> | <a href="/init_db" style="color: white;">Initialize DB</a></p>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/test')
def test():
    return "Flask app is working! 🎉"

@app.route('/test_signup')
def test_signup():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Signup - C2 Game Zone</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .test-container {
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                color: white;
                width: 100%;
                max-width: 400px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            input {
                width: 100%;
                padding: 10px;
                border: none;
                border-radius: 5px;
                background: rgba(255,255,255,0.2);
                color: white;
                box-sizing: border-box;
            }
            input::placeholder {
                color: rgba(255,255,255,0.7);
            }
            button {
                width: 100%;
                padding: 15px;
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: rgba(255,255,255,0.3);
            }
            .result {
                margin-top: 20px;
                padding: 10px;
                border-radius: 5px;
                background: rgba(255,255,255,0.1);
            }
        </style>
    </head>
    <body>
        <div class="test-container">
            <h2 style="text-align: center; margin-bottom: 30px;">🧪 Test Signup</h2>
            <form id="testSignupForm">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required placeholder="Enter your email">
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required placeholder="Enter password">
                </div>
                <button type="submit">Test Signup</button>
            </form>
            <div id="result" class="result" style="display: none;"></div>
        </div>
        <script>
            document.getElementById('testSignupForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const username = document.getElementById('username').value;
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '🔄 Testing signup...';
                
                fetch('/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: username,
                        email: email,
                        password: password
                    })
                })
                .then(response => {
                    console.log('Response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('Response data:', data);
                    if (data.success) {
                        resultDiv.innerHTML = `✅ Success! ${data.message}`;
                        setTimeout(() => {
                            if (data.redirect) {
                                window.location.href = data.redirect;
                            } else {
                                window.location.href = '/home';
                            }
                        }, 2000);
                    } else {
                        resultDiv.innerHTML = `❌ Error: ${data.error}`;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    resultDiv.innerHTML = `❌ Network Error: ${error.message}`;
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/init_db')
def init_db_route():
    try:
        init_database()
        return jsonify({'success': True, 'message': 'Database initialized successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/home')
def home():
    try:
        print("Home route accessed")  # Debug log
        
        if 'user_id' not in session:
            print("No user_id in session, redirecting to login")  # Debug log
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user:
            print("User not found, clearing session")  # Debug log
            session.clear()
            return redirect(url_for('login'))
        
        print(f"Rendering home page for user: {user.username}")  # Debug log
        
        # Try to render template, if it fails, return simple HTML
        try:
            return render_template('home.html', user=user)
        except Exception as template_error:
            print(f"Template error: {template_error}")  # Debug log
            # Return simple HTML as fallback
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>C2 Game Zone - Home</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin: 0; min-height: 100vh; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .welcome {{ font-size: 32px; margin-bottom: 30px; text-align: center; }}
                    .games {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }}
                    .game {{ padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; text-align: center; cursor: pointer; transition: transform 0.3s; }}
                    .game:hover {{ transform: translateY(-5px); }}
                    .logout {{ text-align: center; margin-top: 30px; }}
                    .logout a {{ color: white; text-decoration: none; padding: 10px 20px; background: rgba(255,255,255,0.2); border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="welcome">🎮 Welcome, {user.username}!</div>
                    <div class="games">
                        <div class="game">🎯 2048</div>
                        <div class="game">🐍 Snake</div>
                        <div class="game">♟️ Chess</div>
                        <div class="game">🐦 Flappy Bird</div>
                        <div class="game">🧠 Memory Game</div>
                        <div class="game">🎲 Tic Tac Toe</div>
                        <div class="game">🏓 Pong</div>
                        <div class="game">🎪 Tetris</div>
                    </div>
                    <div class="logout">
                        <a href="/logout">Logout</a>
                    </div>
                </div>
            </body>
            </html>
            """
    except Exception as e:
        print(f"Error in home route: {e}")  # Debug log
        return f"Error loading home page: {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Ensure database is initialized
            try:
                with app.app_context():
                    db.create_all()
                    print("✅ Database tables ensured during login")
            except Exception as db_error:
                print(f"⚠️ Database check error: {db_error}")
            
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            print(f"Login attempt for email: {email}")  # Debug log
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['username'] = user.username
                print(f"Login successful for user: {user.username}")  # Debug log
                return jsonify({'success': True, 'redirect': url_for('home')})
            else:
                print(f"Login failed for email: {email}")  # Debug log
                return jsonify({'success': False, 'error': 'Invalid email or password'})
        except Exception as e:
            print(f"Login error: {e}")  # Debug log
            return jsonify({'success': False, 'error': f'Login error: {str(e)}'})
    
    try:
        return render_template('login.html')
    except Exception as e:
        # Return simple login form if template is missing
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - C2 Game Zone</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .login-container {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                    color: white;
                    width: 100%;
                    max-width: 400px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                }
                input {
                    width: 100%;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                    background: rgba(255,255,255,0.2);
                    color: white;
                    box-sizing: border-box;
                }
                input::placeholder {
                    color: rgba(255,255,255,0.7);
                }
                button {
                    width: 100%;
                    padding: 15px;
                    background: rgba(255,255,255,0.2);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }
                button:hover {
                    background: rgba(255,255,255,0.3);
                }
                .links {
                    text-align: center;
                    margin-top: 20px;
                }
                .links a {
                    color: white;
                    text-decoration: none;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h2 style="text-align: center; margin-bottom: 30px;">🎮 Login</h2>
                <form id="loginForm">
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required placeholder="Enter your email">
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required placeholder="Enter your password">
                    </div>
                    <button type="submit">Login</button>
                </form>
                <div class="links">
                    <a href="/signup">Don't have an account? Sign up</a>
                </div>
            </div>
            <script>
                document.getElementById('loginForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const email = document.getElementById('email').value;
                    const password = document.getElementById('password').value;
                    
                    fetch('/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            email: email,
                            password: password
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Login successful!');
                            if (data.redirect) {
                                window.location.href = data.redirect;
                            } else {
                                window.location.href = '/home';
                            }
                        } else {
                            alert(data.error || 'Login failed');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Network error. Please check your connection.');
                    });
                });
            </script>
        </body>
        </html>
        """

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            print("🔄 Signup request received")  # Debug log
            
            # Ensure database is initialized
            try:
                with app.app_context():
                    db.create_all()
                    print("✅ Database tables ensured during signup")
            except Exception as db_error:
                print(f"⚠️ Database check error: {db_error}")
            
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            print(f"📝 Signup attempt for: {username} ({email})")  # Debug log
            
            # Validate input
            if not username or not email or not password:
                return jsonify({'success': False, 'error': 'All fields are required'})
            
            # Check if user already exists
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                print(f"❌ User already exists: {username} or {email}")  # Debug log
                return jsonify({'success': False, 'error': 'Username or email already exists'})
            
            # Create new user
            password_hash = generate_password_hash(password)
            new_user = User(username=username, email=email, password_hash=password_hash)
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f"✅ User created successfully: {username}")  # Debug log
            
            # Log in the user
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            
            print(f"✅ User logged in: {username}")  # Debug log
            
            return jsonify({
                'success': True, 
                'message': 'Account created successfully! Welcome to C2 Game Zone!',
                'redirect': url_for('home')
            })
        except Exception as e:
            db.session.rollback()
            error_msg = f'Signup error: {str(e)}'
            print(f"❌ {error_msg}")  # Debug log
            print(traceback.format_exc())  # Full error trace
            return jsonify({'success': False, 'error': error_msg})
    
    try:
        return render_template('signup.html')
    except Exception as e:
        # Return simple signup form if template is missing
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sign Up - C2 Game Zone</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .signup-container {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                    color: white;
                    width: 100%;
                    max-width: 400px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                }
                input {
                    width: 100%;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                    background: rgba(255,255,255,0.2);
                    color: white;
                    box-sizing: border-box;
                }
                input::placeholder {
                    color: rgba(255,255,255,0.7);
                }
                button {
                    width: 100%;
                    padding: 15px;
                    background: rgba(255,255,255,0.2);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }
                button:hover {
                    background: rgba(255,255,255,0.3);
                }
                .links {
                    text-align: center;
                    margin-top: 20px;
                }
                .links a {
                    color: white;
                    text-decoration: none;
                }
            </style>
        </head>
        <body>
            <div class="signup-container">
                <h2 style="text-align: center; margin-bottom: 30px;">🎮 Create Account</h2>
                <form id="signupForm">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required placeholder="Enter username">
                    </div>
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required placeholder="Enter your email">
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required placeholder="Enter password">
                    </div>
                    <button type="submit">Create Account</button>
                </form>
                <div class="links">
                    <a href="/login">Already have an account? Login</a>
                </div>
            </div>
            <script>
                document.getElementById('signupForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const username = document.getElementById('username').value;
                    const email = document.getElementById('email').value;
                    const password = document.getElementById('password').value;
                    
                    fetch('/signup', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            username: username,
                            email: email,
                            password: password
                        })
                    })
                    .then(response => response.json())
                                         .then(data => {
                         if (data.success) {
                             alert('Account created successfully! Welcome to C2 Game Zone!');
                             if (data.redirect) {
                                 window.location.href = data.redirect;
                             } else {
                                 window.location.href = '/home';
                             }
                         } else {
                             alert(data.error || 'Signup failed');
                         }
                     })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Network error. Please check your connection.');
                    });
                });
            </script>
        </body>
        </html>
        """

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

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Production settings for Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 