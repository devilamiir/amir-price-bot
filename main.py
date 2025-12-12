import requests
import time
import telebot
import threading
import json
import os

TOKEN = "8525628377:AAG-Ut-S6qTRt_MTXAHK_sl2xYndDV0smrU"
bot = telebot.TeleBot(TOKEN)

# --------------------------
# بخش مدیریت کاربر – ذخیره chat_id
# --------------------------

USERS_FILE = "users.json"
ADMIN_ID = 714402925   # آیدی ادمین

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

# --------------------------
# کد اصلی ربات قیمت دلار
# --------------------------

AUTO_SEND = True
CHAT_ID = None
MESSAGE_ID = None

API_URL = "https://api.zipodo.ir/usdt/"

def get_dollar_price():
    try:
        resp = requests.get(API_URL, timeout=10).json()
        price = resp.get("price")
        if price is not None:
            return f"💵 قیمت دلار: {int(price):,} تومان"
        else:
            return "⚠️ خطا: قیمت یافت نشد!"
    except requests.exceptions.RequestException:
        return "❌ خطا در اتصال به API!"
    except Exception as e:
        return f"❌ خطا در پردازش داده: {e}"

def auto_sender():
    global CHAT_ID, MESSAGE_ID
    while True:
        if AUTO_SEND and CHAT_ID:
            text = get_dollar_price()
            try:
                if MESSAGE_ID:
                    bot.edit_message_text(chat_id=CHAT_ID, message_id=MESSAGE_ID, text=text)
                else:
                    msg = bot.send_message(CHAT_ID, text)
                    MESSAGE_ID = msg.message_id
            except telebot.apihelper.ApiException:
                msg = bot.send_message(CHAT_ID, text)
                MESSAGE_ID = msg.message_id
        time.sleep(10)

threading.Thread(target=auto_sender, daemon=True).start()

# --------------------------
# دستورات کاربر
# --------------------------

@bot.message_handler(commands=["start"])
def start(msg):
    global CHAT_ID, MESSAGE_ID
    CHAT_ID = msg.chat.id
    MESSAGE_ID = None

    save_user(msg.chat.id)

    bot.send_message(
        msg.chat.id,
        "ربات قیمت دلار فعال شد ✔️\nقیمت دلار هر ۱۰ ثانیه آپدیت می‌شود."
    )

@bot.message_handler(commands=["price"])
def price(msg):
    bot.send_message(msg.chat.id, get_dollar_price())

# --------------------------
# دستورات ادمین
# --------------------------

@bot.message_handler(commands=["users"])
def show_users(msg):
    if msg.chat.id != ADMIN_ID:
        return
    users = load_users()
    bot.send_message(msg.chat.id, f"👥 تعداد کاربران ربات: {len(users)} نفر")

@bot.message_handler(commands=["broadcast"])
def broadcast(msg):
    if msg.chat.id != ADMIN_ID:
        return bot.reply_to(msg, "❌ شما ادمین نیستید.")

    bot.send_message(msg.chat.id, "متن پیام همگانی را بفرست:")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(msg):
    text = msg.text
    users = load_users()

    sent = 0

    for uid in users:
        try:
            bot.send_message(uid, text)
            sent += 1
        except:
            pass

    bot.send_message(msg.chat.id, f"پیام به {sent} کاربر ارسال شد ✔️🔥")

# --------------------------

bot.infinity_polling()
