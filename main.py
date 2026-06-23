import telebot
import os
import time

print("--- جاري بدء تشغيل البوت ---")

TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("!!! خطأ: لم يتم العثور على BOT_TOKEN !!!")
    exit()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "البوت يعمل بنجاح! 🚀")
    print(f"تم استقبال أمر /start من المستخدم: {message.chat.id}")

print("--- البوت الآن يعمل وينتظر رسائل ---")
# نستخدم infinity_polling لضمان عدم توقف البوت
bot.infinity_polling()
