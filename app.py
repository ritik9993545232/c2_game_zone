from flask import Flask
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

@app.route('/')
def index():
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
                <p><a href="/test" style="color: white;">Test Route</a> | <a href="/health" style="color: white;">Health Check</a></p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/test')
def test():
    return "Test route is working! 🎉"

@app.route('/health')
def health():
    return "OK - Server is healthy! 💚"

@app.route('/login')
def login():
    return "Login page coming soon! 🔐"

@app.route('/signup')
def signup():
    return "Signup page coming soon! 📝"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
