# C2 Game Zone - Flask Web Application

A modern web-based gaming platform built with Python Flask, featuring user authentication, game progress tracking, and a beautiful responsive UI.

## Features

- 🔐 **User Authentication**: Secure login and signup system with password hashing
- 🎮 **Game Collection**: Access to multiple HTML5 games
- 📊 **Progress Tracking**: Save and track game progress and scores with automatic persistence
- 👤 **User Profiles**: View personal statistics and game history
- 🛡️ **Admin Panel**: Complete admin dashboard with user and progress management
- 🎨 **Modern UI**: Beautiful, responsive design with animations
- 🔒 **Session Management**: Secure session handling
- 📱 **Mobile Responsive**: Works on all devices
- 🔄 **Progress Continuity**: Continue games from where you left off

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (with SQLAlchemy ORM)
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Werkzeug password hashing
- **Styling**: Custom CSS with gradients and animations

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd C2_GAME_ZONE

# Or simply download and extract the project files
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 4: Access the Application

Open your web browser and navigate to:
- **Homepage**: `http://localhost:5000`
- **Login**: `http://localhost:5000/login`
- **Signup**: `http://localhost:5000/signup`

## Database Setup

The application automatically creates the database and tables on first run. The database file (`c2_game_zone.db`) will be created in the project root directory.

### Database Schema

- **users**: User accounts with username, email, and hashed passwords
- **game_progress**: Game progress tracking with scores and timestamps

## Project Structure

```
C2_GAME_ZONE/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── c2_game_zone.db       # SQLite database (created automatically)
├── templates/            # HTML templates
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── signup.html       # Signup page
│   ├── home.html         # Main game hub
│   └── profile.html      # User profile page
├── static/               # Static files
│   └── images/           # Images and assets
└── Files/                # Original game files
    ├── GAME_FILES/       # HTML5 games
    ├── HTML_FILES/       # Original HTML files
    ├── IMAGES/           # Game images
    └── ...
```

## Usage

### For Users

1. **Create Account**: Visit the signup page to create a new account
2. **Login**: Use your email and password to access your account
3. **Play Games**: Browse and play games from the home page
4. **Track Progress**: Your game progress is automatically saved
5. **View Profile**: Check your statistics and game history

### For Developers

#### Adding New Games

1. Place your HTML5 game files in the `Files/GAME_FILES/` directory
2. Update the game grid in `templates/home.html`
3. Add game images to `static/images/`
4. Include the progress manager in your game:
   ```html
   <script src="/static/js/game-progress.js"></script>
   <script>
       const progressManager = createGameProgressManager('YourGameName');
       // Load progress when game starts
       progressManager.loadProgress().then(progress => {
           // Initialize game with saved progress
       });
   </script>
   ```

#### Customizing the UI

- Modify CSS styles in the template files
- Update the color scheme in the CSS variables
- Add new animations and effects

#### Database Modifications

- Update the models in `app.py`
- Run database migrations if needed
- Test the changes thoroughly

## API Endpoints

### Authentication
- `GET /` - Landing page
- `GET /login` - Login page
- `POST /login` - Login API
- `GET /signup` - Signup page
- `POST /signup` - Signup API
- `GET /logout` - Logout

### User Management
- `GET /home` - Main game hub (requires login)
- `GET /user_profile` - User profile page
- `GET /check_auth` - Check authentication status

### Game Progress
- `POST /save_progress` - Save game progress (with level, lives, game state)
- `GET /get_progress/<game_name>` - Get game progress

### Admin Panel
- `GET /admin` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/progress` - Progress management
- `POST /admin/create_admin` - Create new admin user

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection (built into Flask)
- Input validation and sanitization
- Secure cookie handling

## Customization

### Changing the Database

To use a different database (MySQL, PostgreSQL):

1. Update the database URI in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/dbname'
```

2. Install the appropriate database driver:
```bash
pip install mysqlclient  # For MySQL
pip install psycopg2-binary  # For PostgreSQL
```

### Adding New Features

1. **New Routes**: Add routes in `app.py`
2. **New Templates**: Create HTML templates in `templates/`
3. **New Models**: Add database models in `app.py`
4. **Static Files**: Add CSS/JS files in `static/`

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change the port in app.py
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Database Errors**
   ```bash
   # Delete the database file and restart
   rm c2_game_zone.db
   python app.py
   ```

3. **Import Errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

### Debug Mode

The application runs in debug mode by default. For production:

1. Set `debug=False` in `app.py`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure proper logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Future Enhancements

- [ ] Multiplayer game support
- [ ] Leaderboards and rankings
- [ ] Social features (friends, chat)
- [ ] Game achievements system
- [ ] API for third-party integrations
- [ ] Mobile app development
- [ ] Real-time notifications
- [ ] Game categories and filtering
- [ ] User-generated content
- [ ] Advanced analytics and reporting
- [ ] Game tournaments and events
- [ ] Cloud save synchronization

---

**Happy Gaming! 🎮** 