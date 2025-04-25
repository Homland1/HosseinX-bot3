import os
import logging
import sys
import threading
import time
import json
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
bot_instance = None
is_running = False
bot_thread = None

# Import models here to avoid circular imports
from models import BotLog, BotUser, BotMessage
from app import db

# Function to add log entries to the database
def add_log(level, message):
    from app import app
    with app.app_context():
        log_entry = BotLog(level=level, message=message)
        db.session.add(log_entry)
        db.session.commit()

# Function to send a message using the Telegram Bot API
def send_telegram_message(token, chat_id, text, reply_markup=None):
    """Send a message using the Telegram Bot API"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None
        
# Function to create an inline keyboard with a Mini App button
def create_webapp_button(web_app_url, button_text="Open Mini App"):
    """Create a keyboard with a Web App button"""
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": button_text,
                    "web_app": {
                        "url": web_app_url
                    }
                }
            ]
        ]
    }
    return keyboard

# Function to get bot updates using the Telegram Bot API
def get_telegram_updates(token, offset=None):
    """Get updates from the Telegram Bot API"""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"timeout": 30}
    
    if offset:
        params["offset"] = offset
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return None

# Function to get bot information using the Telegram Bot API
def get_bot_info(token):
    """Get bot information using the Telegram Bot API"""
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error getting bot info: {e}")
        return None

# Function to simulate bot polling
def simulate_bot_polling(token):
    """Simulate bot polling in a separate thread."""
    global is_running
    
    add_log("INFO", f"Starting bot simulation with token: {token[:5]}...{token[-5:]}")
    
    # Check if we can get bot info
    bot_info = get_bot_info(token)
    if bot_info and bot_info.get('ok'):
        bot_username = bot_info['result']['username']
        add_log("INFO", f"Connected to bot: @{bot_username}")
    else:
        add_log("WARNING", "Could not connect to Telegram API, running in simulation mode only")
    
    # Create demo users for simulation
    from app import app
    with app.app_context():
        # Check if we have demo users already
        if BotUser.query.count() == 0:
            # Add some demo users
            demo_users = [
                {"telegram_id": 123456789, "username": "demo_user1", "first_name": "Demo", "last_name": "User1"},
                {"telegram_id": 987654321, "username": "demo_user2", "first_name": "Demo", "last_name": "User2"}
            ]
            
            for user_data in demo_users:
                user = BotUser(**user_data)
                db.session.add(user)
            
            # Add some demo messages
            demo_messages = [
                {"telegram_user_id": 123456789, "message_text": "/start", "is_from_user": True},
                {"telegram_user_id": 123456789, "message_text": "Hello Demo User1! 👋\n\nWelcome to HosseinX-bot3. I'm here to assist you.\n\nUse /help to see available commands.", "is_from_user": False},
                {"telegram_user_id": 987654321, "message_text": "Hello bot!", "is_from_user": True},
                {"telegram_user_id": 987654321, "message_text": "You said: Hello bot!", "is_from_user": False}
            ]
            
            for msg_data in demo_messages:
                message = BotMessage(**msg_data)
                db.session.add(message)
            
            db.session.commit()
            add_log("INFO", "Added demo users and messages")
    
    # Try to poll for real updates
    last_update_id = None
    
    # Keep the bot running while is_running is True
    while is_running:
        try:
            # Try to get real updates from Telegram
            if token and token != "simulation":
                updates = get_telegram_updates(token, last_update_id)
                
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        handle_update(token, update)
                        # Update the last update ID
                        last_update_id = update['update_id'] + 1
            
            # Sleep to prevent CPU usage spikes
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error in bot simulation: {e}")
            add_log("ERROR", f"Error in bot simulation: {str(e)}")
            time.sleep(5)  # Wait longer if there's an error

# Function to handle a Telegram update
def handle_update(token, update):
    """Handle a single update from Telegram"""
    from app import app
    
    try:
        # Check if this is a message
        if 'message' in update and 'text' in update['message']:
            chat_id = update['message']['chat']['id']
            user_id = update['message']['from']['id']
            text = update['message']['text']
            username = update['message'].get('from', {}).get('username', '')
            first_name = update['message'].get('from', {}).get('first_name', '')
            last_name = update['message'].get('from', {}).get('last_name', '')
            
            # Log the received message
            with app.app_context():
                # Check if user exists
                user = BotUser.query.filter_by(telegram_id=user_id).first()
                if not user:
                    # Create new user
                    user = BotUser(
                        telegram_id=user_id,
                        username=username,
                        first_name=first_name,
                        last_name=last_name
                    )
                    db.session.add(user)
                    db.session.commit()
                    add_log("INFO", f"New user registered: {user_id} - {username}")
                
                # Save the message
                message = BotMessage(
                    telegram_user_id=user_id,
                    message_text=text,
                    is_from_user=True
                )
                db.session.add(message)
                db.session.commit()
            
            # Handle commands
            if text.startswith('/'):
                command = text.split(' ')[0].lower()
                
                if command == '/start':
                    welcome_message = (
                        f"به بازی حسین ایکس بات ۳ خوش آمدید {first_name}! 👋\n\n"
                        f"من اینجا هستم تا به شما کمک کنم.\n\n"
                        f"برای دیدن دستورات از /help استفاده کنید یا مینی اپ را از دکمه زیر باز کنید."
                    )
                    
                    # Create a Mini App button
                    # 1. First option: Use GitHub Pages (when available)
                    github_url = "homland1.github.io/HosseinX-bot3"
                    
                    # 2. Fallback to Replit URL if GitHub Pages is not ready
                    replit_domain = os.environ.get('REPLIT_DOMAINS', '57a0603e-812d-4af0-a6fd-47ceb27f1626-00-365m8arhc6yga.picard.replit.dev')
                    if ',' in replit_domain:  # Handle multiple domains
                        replit_domain = replit_domain.split(',')[0]
                    
                    # 3. Choose which URL to use (for now use Replit URL)
                    use_github = False  # Set to True when GitHub Pages is ready
                    
                    if use_github:
                        webapp_url = f"https://{github_url}/miniapp/?user_id={user_id}"
                    else:
                        webapp_url = f"https://{replit_domain}/telegram-miniapp/index.html?user_id={user_id}"
                    
                    keyboard = create_webapp_button(webapp_url, "باز کردن مینی اپ حسین ایکس بات")
                    
                    # Send welcome message with Mini App button
                    send_telegram_message(token, chat_id, welcome_message, keyboard)
                    
                    # Log the bot's response
                    with app.app_context():
                        bot_message = BotMessage(
                            telegram_user_id=user_id,
                            message_text=welcome_message + "\n[Mini App Button Added]",
                            is_from_user=False
                        )
                        db.session.add(bot_message)
                        db.session.commit()
                
                elif command == '/help':
                    help_text = (
                        "دستورات قابل استفاده:\n\n"
                        "/start - شروع مجدد ربات\n"
                        "/help - نمایش این پیام راهنما\n"
                        "/about - درباره این ربات\n"
                    )
                    send_telegram_message(token, chat_id, help_text)
                    
                    # Log the bot's response
                    with app.app_context():
                        bot_message = BotMessage(
                            telegram_user_id=user_id,
                            message_text=help_text,
                            is_from_user=False
                        )
                        db.session.add(bot_message)
                        db.session.commit()
                
                elif command == '/about':
                    about_text = (
                        "🤖 حسین ایکس بات ۳\n\n"
                        "یک ربات تلگرام ساخته شده با پایتون.\n"
                        "توسعه داده شده برای سرگرمی و بازی."
                    )
                    send_telegram_message(token, chat_id, about_text)
                    
                    # Log the bot's response
                    with app.app_context():
                        bot_message = BotMessage(
                            telegram_user_id=user_id,
                            message_text=about_text,
                            is_from_user=False
                        )
                        db.session.add(bot_message)
                        db.session.commit()
            
            else:
                # Echo back for regular messages
                response = f"شما گفتید: {text}"
                send_telegram_message(token, chat_id, response)
                
                # Log the bot's response
                with app.app_context():
                    bot_message = BotMessage(
                        telegram_user_id=user_id,
                        message_text=response,
                        is_from_user=False
                    )
                    db.session.add(bot_message)
                    db.session.commit()
    
    except Exception as e:
        logger.error(f"Error handling update: {e}")
        add_log("ERROR", f"Error handling update: {str(e)}")

def start_bot(token):
    """Start the Telegram bot with the given token"""
    global is_running, bot_thread
    
    try:
        if is_running:
            logger.info("Bot is already running")
            return True
        
        # Set bot as running
        is_running = True
        
        # Start the bot in a separate thread
        bot_thread = threading.Thread(target=simulate_bot_polling, args=(token,), daemon=True)
        bot_thread.start()
        
        add_log("INFO", "Bot started successfully")
        return True
    except Exception as e:
        add_log("ERROR", f"Failed to start bot: {str(e)}")
        logger.error(f"Failed to start bot: {e}")
        is_running = False
        return False

def stop_bot():
    """Stop the bot if it's running"""
    global is_running, bot_thread
    
    if is_running:
        try:
            # Stop the bot thread
            is_running = False
            
            # Wait for thread to finish if it exists
            if bot_thread and bot_thread.is_alive():
                bot_thread.join(timeout=2.0)
            
            add_log("INFO", "Bot stopped")
            return True
        except Exception as e:
            add_log("ERROR", f"Error stopping bot: {str(e)}")
            logger.error(f"Error stopping bot: {e}")
            return False
    else:
        logger.info("Bot is not running")
        return False

def get_bot_status():
    """Get the current status of the bot"""
    global is_running
    return {
        "is_running": is_running
    }
