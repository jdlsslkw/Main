import telebot
from telebot import types
import os

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

bot = telebot.TeleBot(TOKEN)

# 1. دالة إنشاء القائمة الرئيسية
def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ نشر حساب جديد", callback_data="post_new"))
    markup.add(types.InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats"))
    markup.add(types.InlineKeyboardButton("ℹ️ المساعدة", callback_data="help"))
    return markup

# 2. أمر البداية
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "مرحباً بك في بوت النشر! اختر ما تريد من القائمة:", reply_markup=main_menu())

# 3. استقبال ضغطات الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "post_new":
        bot.send_message(call.message.chat.id, "الرجاء إرسال تفاصيل الحساب (اليوزر، السعر، المميزات):")
        # هنا البوت ينتظر الرسالة القادمة من المستخدم
        bot.register_next_step_handler(call.message, get_post_details)
        
    elif call.data == "my_stats":
        bot.send_message(call.message.chat.id, "إحصائياتك: \n- الحسابات المنشورة: 0\n- الحسابات المباعة: 0")
        
    elif call.data == "help":
        bot.send_message(call.message.chat.id, "أرسل /start لإظهار القائمة.")

# 4. استقبال البيانات بعد ضغط زر "نشر"
def get_post_details(message):
    user_data = message.text
    user_name = message.from_user.username
    
    # إرسال للإدارة للموافقة
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ قبول ونشر", callback_data=f"approve_{message.chat.id}"))
    markup.add(types.InlineKeyboardButton("❌ رفض", callback_data="reject"))
    
    bot.send_message(ADMIN_ID, f"📩 طلب جديد من @{user_name}:\n\n{user_data}", reply_markup=markup)
    bot.reply_to(message, "تم إرسال طلبك للإدارة بنجاح ✅")

bot.polling()
