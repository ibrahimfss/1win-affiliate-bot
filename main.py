from flask import Flask, request
import telebot
import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

AFFILIATE_LINK = "https://1wyvrz.life/casino/list?open=register&p=wjud"
PROMOCODE = "OGGY"
MIN_DEPOSIT = 10

app = Flask(__name__)
verified_users = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('English', 'Hindi')
    bot.send_message(message.chat.id, "Select your language / अपनी भाषा चुनें:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['English', 'Hindi'])
def main_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Instructions', 'Registration', 'Get Signal')
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Instructions')
def instructions(message):
    text = f"""
Step 1: Open 1Win official website.
Step 2: Click Register.
Step 3: Use promocode: {PROMOCODE}
Step 4: Complete registration and make a minimum deposit of ${MIN_DEPOSIT}.
"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == 'Registration')
def registration(message):
    markup = telebot.types.InlineKeyboardMarkup()
    link = telebot.types.InlineKeyboardButton("Register Here", url=AFFILIATE_LINK)
    markup.add(link)
    bot.send_message(message.chat.id, "Click below to register via my affiliate link:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Get Signal')
def get_signal(message):
    msg = bot.send_message(message.chat.id, "Please enter your 1Win Player ID for verification:")
    bot.register_next_step_handler(msg, verify_user)

def verify_user(message):
    user_id = message.text
    POSTBACK_URL = "https://your-postback-url.com/api/postback"

    try:
        response = requests.get(f"{POSTBACK_URL}?user_id={user_id}")
        data = response.json()
        if data.get("affiliate") == "wjud" and float(data.get("amount",0)) >= MIN_DEPOSIT:
            verified_users[message.chat.id] = user_id
            bot.send_message(message.chat.id, "✅ Verified! You will start receiving signals.")
        else:
            bot.send_message(message.chat.id, f"❌ Not verified. Register via my link and deposit at least ${MIN_DEPOSIT}.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Verification failed. Try again later.\nError: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

@app.route('/')
def index():
    return "Bot is running", 200

def send_signal(signal_text):
    for chat_id in verified_users:
        bot.send_message(chat_id, signal_text)

if __name__ == "__main__":
    app.run()
