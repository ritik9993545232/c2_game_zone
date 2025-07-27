from flask import Flask, render_template_string
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
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .logo { font-size: 48px; color: #333; margin-bottom: 20px; }
            .subtitle { font-size: 24px; color: #666; margin-bottom: 40px; }
            .btn { display: inline-block; padding: 15px 30px; margin: 10px; 
                   background: #007bff; color: white; text-decoration: none; 
                   border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="logo">🎮 C2 Game Zone</div>
        <div class="subtitle">Your Gaming Hub</div>
        <a href="/login" class="btn">Sign In</a>
        <a href="/signup" class="btn">Create Account</a>
        <p><a href="/test">Test Route</a> | <a href="/health">Health Check</a></p>
    </body>
    </html>
    """

@app.route('/test')
def test():
    return "Test route is working!"

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 