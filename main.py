import requests
import time
import telebot
import threading

# توکن ربات خودت
TOKEN = "8525628377:AAG-Ut-S6qTRt_MTXAHK_sl2xYndDV0smrU"
bot = telebot.TeleBot(TOKEN)

AUTO_SEND = True   # ارسال خودکار
CHAT_ID = None     # بعد از اولین پیام ذخیره می‌شود

def get_prices():
    try:
        # دلار از نوبیتکس
        dollar = requests.get("https://api.nobitex.ir/market/stats").json()["stats"]["USDTIRT"]["bestSell"]
        dollar = int(float(dollar))

        # دلار سنا
        sana = requests.get("https://api.tgju.online/v1/data/sana").json()["sana_buy_usd"]

        return (
            f"💵 دلار نوبیتکس: {dollar:,} تومان\n"
            f"🟡 دلار سنا: {sana:,} تومان"
        )

    except Exception as e:
        return "❌ خطا در دریافت قیمت!"

def auto_sender():
    global CHAT_ID
    while True:
        if AUTO_SEND and CHAT_ID:
            bot.send_message(CHAT_ID, get_prices())
        time.sleep(10)  # هر 10 ثانیه

threading.Thread(target=auto_sender, daemon=True).start()

@bot.message_handler(commands=["start"])
def start(msg):
    global CHAT_ID
    CHAT_ID = msg.chat.id
    bot.send_message(msg.chat.id, "🟢 ربات قیمت فعال شد.\nهر 10 ثانیه قیمت رو برات می‌فرستم.")

@bot.message_handler(commands=["price"])
def price(msg):
    bot.send_message(msg.chat.id, get_prices())

bot.infinity_polling()
