import telebot
import os

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def get_file_id(message):
    # هذا الكود سيأخذ آخر صورة ترسلها ويعطيك الـ ID الخاص بها
    file_id = message.photo[-1].file_id
    bot.reply_to(message, f"هذا هو كود الصورة (انسخه واحفظه عندك):\n\n`{file_id}`")

bot.polling()
