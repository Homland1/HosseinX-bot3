import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import threading
from datetime import datetime

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up database base class
class Base(DeclarativeBase):
    pass

# Initialize Flask app and database
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import User, BotLog, BotSetting
from bot import start_bot, stop_bot, get_bot_status

# Add context processor for templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create database tables
with app.app_context():
    db.create_all()
    
    # Check if admin user exists, create one if not
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        
        # Add default bot settings
        token_setting = BotSetting(
            key='telegram_token',
            value=os.environ.get('TELEGRAM_TOKEN', '8149810684:AAGwHuOnuuXt1EEFicGvXgTIx72H7_xCOzg')
        )
        db.session.add(token_setting)
        
        # Create initial log entry
        initial_log = BotLog(
            level='INFO',
            message='Bot system initialized'
        )
        db.session.add(initial_log)
        
        db.session.commit()
        logger.info("Created admin user and initial settings")

# Bot thread
bot_thread = None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/miniapp')
def miniapp():
    """Telegram Mini App endpoint"""
    from models import BotUser
    
    user_id = request.args.get('user_id')
    telegram_user = None
    
    if user_id:
        try:
            user_id = int(user_id)
            telegram_user = BotUser.query.filter_by(telegram_id=user_id).first()
        except (ValueError, TypeError):
            pass
    
    return render_template('miniapp.html', user=telegram_user)

# Serve static files for the Telegram Mini App
@app.route('/telegram-miniapp/<path:path>')
def telegram_miniapp(path):
    """Serve the Telegram Mini App static files"""
    return send_from_directory('static/telegram-miniapp', path)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    bot_status = get_bot_status()
    logs = BotLog.query.order_by(BotLog.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', bot_status=bot_status, logs=logs)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        token = request.form.get('telegram_token')
        
        # Update token in database
        token_setting = BotSetting.query.filter_by(key='telegram_token').first()
        if token_setting:
            token_setting.value = token
        else:
            token_setting = BotSetting(key='telegram_token', value=token)
            db.session.add(token_setting)
        
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('settings'))
    
    # Get current settings
    settings = {}
    for setting in BotSetting.query.all():
        settings[setting.key] = setting.value
    
    return render_template('settings.html', settings=settings)

@app.route('/logs')
@login_required
def logs():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    logs_pagination = BotLog.query.order_by(BotLog.timestamp.desc()).paginate(page=page, per_page=per_page)
    return render_template('logs.html', logs=logs_pagination)

@app.route('/bot/start')
@login_required
def start_bot_route():
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        # Get token from database
        token_setting = BotSetting.query.filter_by(key='telegram_token').first()
        if token_setting:
            token = token_setting.value
            bot_thread = threading.Thread(target=start_bot, args=(token,))
            bot_thread.daemon = True
            bot_thread.start()
            flash('Bot started successfully', 'success')
            
            # Log the bot start
            new_log = BotLog(level='INFO', message='Bot started by user: ' + current_user.username)
            db.session.add(new_log)
            db.session.commit()
        else:
            flash('Telegram token not found in settings', 'danger')
    else:
        flash('Bot is already running', 'info')
    
    return redirect(url_for('dashboard'))

@app.route('/bot/stop')
@login_required
def stop_bot_route():
    if stop_bot():
        flash('Bot stopped successfully', 'success')
        
        # Log the bot stop
        new_log = BotLog(level='INFO', message='Bot stopped by user: ' + current_user.username)
        db.session.add(new_log)
        db.session.commit()
    else:
        flash('Bot is not running', 'info')
    
    return redirect(url_for('dashboard'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error='Internal server error'), 500
