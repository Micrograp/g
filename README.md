# g

Telegram Gallery Bridge — Web client and Flask server with background Telegram bot listener.

## Features
- **Web Gallery Client**: Responsive photo picker interface.
- **Flask Backend**: Upload endpoint with size validation and MIME-type handling.
- **Telegram Bot (`@Ylxgallbot`)**: Auto-replies to `/start` with your chat ID and a direct gallery link.
- **Security**: Environment variable configuration via `.env` with file disclosure protection.

## Setup & Running
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.env`:
   ```bash
   cp .env.example .env
   # Add your TELEGRAM_BOT_TOKEN
   ```
3. Run the server & bot:
   ```bash
   python server.py
   ```
