import os
import threading
from flask import Flask, request, jsonify, send_from_directory, abort
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Max request payload size (32 MB)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}" if TELEGRAM_BOT_TOKEN else None

# Allowlist for safe static file serving
ALLOWED_STATIC_FILES = {'index.html', 'style.css', 'app.js'}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    if filename in ALLOWED_STATIC_FILES:
        return send_from_directory('.', filename)
    abort(404)

@app.route('/upload', methods=['POST'])
def upload():
    if not TELEGRAM_BOT_TOKEN or not API_URL:
        return jsonify({"error": "TELEGRAM_BOT_TOKEN is not configured on the server."}), 500

    user_id = request.form.get('userId', '').strip()
    images = request.files.getlist('images')

    if not user_id:
        return jsonify({"error": "User ID is required."}), 400

    # Ensure user_id is a valid Telegram chat ID (numeric)
    try:
        int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID format. Telegram chat IDs must be numeric."}), 400

    if not images or len(images) == 0:
        return jsonify({"error": "No images were provided."}), 400

    sent_count = 0
    errors = []

    for img in images:
        if not img.filename:
            continue

        try:
            file_bytes = img.read()
            file_size = len(file_bytes)

            if file_size == 0:
                continue

            content_type = img.content_type or 'image/jpeg'

            # Telegram sendPhoto limit is ~10MB; fall back to sendDocument for larger files
            if file_size <= 10 * 1024 * 1024 and content_type.startswith('image/'):
                endpoint = f"{API_URL}/sendPhoto"
                files = {'photo': (img.filename, file_bytes, content_type)}
                params = {
                    'chat_id': user_id,
                    'caption': f"Received: {img.filename}"
                }
            else:
                endpoint = f"{API_URL}/sendDocument"
                files = {'document': (img.filename, file_bytes, content_type)}
                params = {
                    'chat_id': user_id,
                    'caption': f"Received: {img.filename}"
                }

            response = requests.post(endpoint, files=files, data=params, timeout=20)
            
            try:
                resp_data = response.json()
            except ValueError:
                resp_data = {}

            if response.status_code == 200 and resp_data.get('ok'):
                sent_count += 1
            else:
                error_desc = resp_data.get('description', response.text)
                errors.append(f"{img.filename}: {error_desc}")
                print(f"Telegram error for {img.filename}: {error_desc}")

        except Exception as e:
            errors.append(f"{img.filename}: {str(e)}")
            print(f"Exception while uploading {img.filename}: {e}")

    # If all uploads failed, return 502 Bad Gateway
    if sent_count == 0 and errors:
        return jsonify({
            "error": "Failed to send photos to Telegram.",
            "details": errors
        }), 502

    return jsonify({
        "message": "Upload complete.",
        "sent_count": sent_count,
        "errors": errors if errors else None
    }), 200

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # Start bot polling in a background thread so the bot responds to /start
    if os.getenv("RUN_BOT_THREAD", "true").lower() in ("true", "1", "yes"):
        try:
            from bot import bot
            bot_info = bot.get_me()
            print("==================================================")
            print(f"🤖 Telegram Bot @{bot_info.username} is connected!")
            print(f"➡️  Send /start to @{bot_info.username} in Telegram to get your Chat ID.")
            print("==================================================")
            bot_thread = threading.Thread(target=lambda: bot.infinity_polling(skip_pending=True), daemon=True)
            bot_thread.start()
        except Exception as e:
            print(f"⚠️ Could not start Telegram bot thread: {e}")

    print(f"Starting server on http://localhost:{port} (debug={debug_mode})...")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
