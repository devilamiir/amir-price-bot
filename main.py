import requests
import time
import telebot
import threading

TOKEN = "8525628377:AAG-Ut-S6qTRt_MTXAHK_sl2xYndDV0smrU"
bot = telebot.TeleBot(TOKEN)

AUTO_SEND = True
CHAT_ID = None
MESSAGE_ID = None

API_URL = "https://dapi.p3p.repl.co/api/?currency=usd"

def get_dollar_price():
    try:
        resp = requests.get(API_URL, timeout=10).json()
        price = resp.get("Price")
        if price:
            # فرمت هزارگان
            return f"💵 قیمت دلار (TGJU): {int(price):,} تومان"
        else:
            return "⚠️ قیمت دلار یافت نشد!"
    except Exception as e:
        return f"❌ صبر کن دارم اطلاعات پیدا میکنم: {e}"

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

@bot.message_handler(commands=["start"])
def start(msg):
    global CHAT_ID, MESSAGE_ID
    CHAT_ID = msg.chat.id
    MESSAGE_ID = None
    bot.send_message(msg.chat.id, "ربات قیمت دلار فعال شد ✔️\nقیمت دلار رو برات هر ۱۰ ثانیه آپدیت می‌کنم.")

@bot.message_handler(commands=["price"])
def price(msg):
    bot.send_message(msg.chat.id, get_dollar_price())

bot.infinity_polling()
