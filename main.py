import telebot
from telebot import types

# --- الإعدادات ---
TOKEN = '8489451507:AAGBdPeWyPgRzapmneFTfWwKIBcakH5VQNI'
ADMIN_ID = 5939498558  # ضع الأيدي الخاص بك هنا
CHANNEL_ID = '@info_sma' # يوزر القناة (يجب أن يكون البوت مشرفاً فيها)

bot = telebot.TeleBot(TOKEN)

# عند بدء البوت
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أهلاً بك! أرسل بيانات الحساب (يوزر، سعر، تفاصيل) للنشر.")

# استقبال بيانات الحساب من المستخدم
@bot.message_handler(func=lambda message: True)
def get_info(message):
    user_name = message.from_user.username
    text = message.text
    
    # إرسال طلب للإدارة للموافقة
    markup = types.InlineKeyboardMarkup()
    btn_accept = types.InlineKeyboardButton("✅ قبول ونشر", callback_data=f"approve_{message.chat.id}")
    btn_reject = types.InlineKeyboardButton("❌ رفض", callback_data="reject")
    markup.add(btn_accept, btn_reject)
    
    bot.send_message(ADMIN_ID, f"طلب جديد من @{user_name}:\n\n{text}", reply_markup=markup)
    bot.reply_to(message, "تم إرسال طلبك للإدارة، انتظر الموافقة.")

# معالجة الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("approve_"):
        # هنا يتم النشر في القناة
        msg_text = call.message.text.replace("طلب جديد من", "حساب للبيع:")
        
        # أزرار التواصل (الموجودة في صورك)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📩 تواصل معي", url="https://t.me/your_username"))
        
        bot.send_message(CHANNEL_ID, msg_text, reply_markup=markup)
        bot.edit_message_text("✅ تم النشر في القناة", call.message.chat.id, call.message.id)
    
    elif call.data == "reject":
        bot.edit_message_text("❌ تم رفض الطلب", call.message.chat.id, call.message.id)

bot.polling()
