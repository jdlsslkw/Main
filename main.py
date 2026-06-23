import telebot
from telebot import types
import os

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

# تم تعديل الاسم إلى Tellonym مع الاحتفاظ بنفس الـ ID الذي أرسلته
PLATFORM_PHOTOS = {
    "Instagram": "AgACAgIAAxkBAAICz2o6hUhrMvIClV47-Td2CHjKnHlCAAI5Gmsb9TLZSRwj_-DEqPvuAQADAgADeAADPAQ",
    "Snapchat": "AgACAgIAAxkBAAICx2o6hOVdwVBTC3HjlE2PDuYzxV9pAAI0Gmsb9TLZSYb6qauGvFSrAQADAgADeAADPAQ",
    "TikTok": "AgACAgIAAxkBAAICzWo6hSBQWpDxGyP5ovwSyPkOFDy_AAI2Gmsb9TLZSZJ8-6FtHlQOAQADAgADeAADPAQ",
    "Twitter": "AgACAgIAAxkBAAICymo6hPDO_QJ6oigWFSaMoNJrrIxVAAI1Gmsb9TLZSfLFLKIZfLRxAQADAgADeAADPAQ",
    "Telegram": "AgACAgIAAxkBAAICxGo6hNZj__J75aTJmiYfsnDYblyxAAIzGmsb9TLZSb35RNF1Ds-HAQADAgADeAADPAQ",
    "Tellonym": "AgACAgIAAxkBAAICwWo6hLT7exibCQ-sgUabQ1ojZX2SAAIyGmsb9TLZSd8x1WsMzz8eAQADAgADeAADPAQ"
}

bot = telebot.TeleBot(TOKEN)
user_pending_posts = {}

# --- الدوال والقوائم ---
def get_main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Post New Account", callback_data="select_platform"))
    markup.add(types.InlineKeyboardButton("Trusted Middlemen", callback_data="show_mm"))
    return markup

def get_platform_menu():
    markup = types.InlineKeyboardMarkup()
    # تم تعديل الاسم هنا أيضاً
    platforms = ["Instagram", "Snapchat", "TikTok", "Twitter", "Telegram", "Tellonym"]
    for p in platforms:
        markup.add(types.InlineKeyboardButton(p, callback_data=f"platform_{p}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="back_to_main"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    try: bot.answer_callback_query(call.id)
    except: pass

    if call.data == "back_to_main":
        bot.edit_message_text("Welcome. Select an option:", chat_id, call.message.message_id, reply_markup=get_main_menu())
    
    elif call.data == "select_platform":
        bot.edit_message_text("Select the platform:", chat_id, call.message.message_id, reply_markup=get_platform_menu())
    
    elif call.data.startswith("platform_"):
        platform = call.data.split("_")[1]
        user_pending_posts[chat_id] = {"platform": platform}
        bot.edit_message_text(f"Platform: {platform}.\nSend details: Username:Price:Details", chat_id, call.message.message_id)
        bot.register_next_step_handler(call.message, process_details)

    elif call.data.startswith("approve_"):
        target_id = int(call.data.split("_")[1])
        post = user_pending_posts.get(target_id)
        if post:
            msg = f"Platform: {post['platform']}\nUsername: @{post['username']}\nPrice: {post['price']}\nDetails: {post['details']}"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Contact Seller", url=f"https://t.me/{post['username']}"))
            
            photo_id = PLATFORM_PHOTOS.get(post['platform'])
            if photo_id:
                bot.send_photo(CHANNEL_ID, photo_id, caption=msg, reply_markup=markup)
            else:
                bot.send_message(CHANNEL_ID, msg, reply_markup=markup)
                
            bot.edit_message_text("Post published to channel.", chat_id, call.message.message_id)
            if target_id in user_pending_posts: del user_pending_posts[target_id]

def process_details(message):
    try:
        parts = message.text.split(":")
        username, price, details = parts[0], parts[1], parts[2]
        chat_id = message.chat.id
        
        user_pending_posts[chat_id].update({"username": username.replace("@", ""), "price": price, "details": details})
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Approve", callback_data=f"approve_{chat_id}"))
        markup.add(types.InlineKeyboardButton("Reject", callback_data="reject"))
        
        admin_msg = f"New Post Request:\nPlatform: {user_pending_posts[chat_id]['platform']}\n{message.text}"
        bot.send_message(ADMIN_ID, admin_msg, reply_markup=markup)
        bot.reply_to(message, "Your post is sent to admin.")
    except:
        bot.reply_to(message, "Use format: Username:Price:Details")
        bot.register_next_step_handler(message, process_details)

bot.polling()
