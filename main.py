import requests
import time
import telebot
import threading

TOKEN = "8525628377:AAG-Ut-S6qTRt_MTXAHK_sl2xYndDV0smrU"
bot = telebot.TeleBot(TOKEN)

AUTO_SEND = True
CHAT_ID = None
MESSAGE_ID = None  # برای ذخیره پیام و آپدیت آن

def get_prices():
    try:
        # دریافت قیمت دلار نوبیتکس
        nobitex_response = requests.get("https://api.nobitex.ir/market/stats").json()
        dollar = nobitex_response.get("stats", {}).get("USDTIRT", {}).get("bestSell")
        if dollar is None:
            dollar = "ناموجود"
        else:
            dollar = f"{int(float(dollar)):,}"

        # دریافت قیمت طلا TGJU
        gold_response = requests.get("https://api.tgju.online/v1/data/sana").json()
        gold = gold_response.get("sana_buy_usd")
        if gold is None:
            gold = "ناموجود"
        else:
            try:
                gold = f"{float(gold):,}"
            except:
                gold = str(gold)

        return f"💵 دلار نوبیتکس: {dollar}\n🟡 قیمت طلا (سنا): {gold}"

    except requests.exceptions.RequestException:
        return "خطا در اتصال به اینترنت یا API!"
    except Exception as e:
        return f"خطا در پردازش داده‌ها: {e}"

def auto_sender():
    global CHAT_ID, MESSAGE_ID
    while True:
        if AUTO_SEND and CHAT_ID:
            text = get_prices()
            try:
                if MESSAGE_ID:
                    # آپدیت پیام قبلی
                    bot.edit_message_text(chat_id=CHAT_ID, message_id=MESSAGE_ID, text=text)
                else:
                    # ارسال پیام جدید و ذخیره message_id
                    msg = bot.send_message(CHAT_ID, text)
                    MESSAGE_ID = msg.message_id
            except telebot.apihelper.ApiException:
                # اگر پیام قبلی حذف شده باشه، پیام جدید ارسال کن
                msg = bot.send_message(CHAT_ID, text)
                MESSAGE_ID = msg.message_id
        time.sleep(10)

threading.Thread(target=auto_sender, daemon=True).start()

@bot.message_handler(commands=["start"])
def start(msg):
    global CHAT_ID, MESSAGE_ID
    CHAT_ID = msg.chat.id
    MESSAGE_ID = None
    bot.send_message(msg.chat.id, "ربات قیمت فعال شد ✔️\nقیمت‌ها هر ۱۰ ثانیه بروزرسانی می‌شوند.")

@bot.message_handler(commands=["price"])
def price(msg):
    bot.send_message(msg.chat.id, get_prices())

bot.infinity_polling()
