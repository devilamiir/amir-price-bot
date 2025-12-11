import requests
import time
import telebot
import threading

TOKEN = "8525628377:AAG-Ut-S6qTRt_MTXAHK_sl2xYndDV0smrU"
bot = telebot.TeleBot(TOKEN)

AUTO_SEND = True
CHAT_ID = None

def get_prices():
    try:
        # دریافت قیمت دلار نوبیتکس
        nobitex_data = requests.get("https://api.nobitex.ir/market/stats").json()
        dollar = nobitex_data.get("stats", {}).get("USDTIRT", {}).get("bestSell")
        if dollar:
            dollar = f"{int(float(dollar)):,}"
        else:
            dollar = "ناموجود"

        # دریافت قیمت طلا
        gold_data = requests.get("https://api.tgju.online/v1/data/sana").json()
        gold = gold_data.get("sana_buy_usd")
        if gold:
            gold = f"{float(gold):,}"
        else:
            gold = "ناموجود"

        return f"💵 دلار نوبیتکس: {dollar}\n🟡 قیمت طلا (سنا): {gold}"
    except Exception as e:
        return f"خطا در دریافت قیمت! ({e})"

def auto_sender():
    global CHAT_ID
    while True:
        if AUTO_SEND and CHAT_ID:
            bot.send_message(CHAT_ID, get_prices())
        time.sleep(10)

threading.Thread(target=auto_sender, daemon=True).start()

@bot.message_handler(commands=["start"])
def start(msg):
    global CHAT_ID
    CHAT_ID = msg.chat.id
    bot.send_message(msg.chat.id, "ربات قیمت فعال شد ✔️\nبه‌صورت خودکار قیمت‌ها رو برات میفرستم.")

@bot.message_handler(commands=["price"])
def price(msg):
    bot.send_message(msg.chat.id, get_prices())

bot.infinity_polling()
