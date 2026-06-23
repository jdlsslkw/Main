import telebot
from telebot import types
import os

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

bot = telebot.TeleBot(TOKEN)
user_pending_posts = {}

# --- Menus ---
def get_main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Post New Account", callback_data="select_platform"))
    markup.add(types.InlineKeyboardButton("Trusted Middlemen", callback_data="show_mm"))
    return markup

def get_platform_menu():
    markup = types.InlineKeyboardMarkup()
    platforms = ["Instagram", "Snapchat", "TikTok", "Twitter", "Telegram"]
    for p in platforms:
        markup.add(types.InlineKeyboardButton(p, callback_data=f"platform_{p}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="back_to_main"))
    return markup

# --- Safe Edit Function ---
def safe_edit_text(chat_id, message_id, text, reply_markup):
    try:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup)
    except Exception as e:
        # This handles cases where the message is not modified
        pass

# --- Handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome. Please select an option:", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # Safely answer callback to stop loading spinner
    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    chat_id = call.message.chat.id

    if call.data == "back_to_main":
        safe_edit_text(chat_id, call.message.message_id, "Welcome. Please select an option:", get_main_menu())

    elif call.data == "select_platform":
        safe_edit_text(chat_id, call.message.message_id, "Select the platform:", get_platform_menu())

    elif call.data.startswith("platform_"):
        platform = call.data.split("_")[1]
        user_pending_posts[chat_id] = {"platform": platform}
        safe_edit_text(chat_id, call.message.message_id, f"Selected: {platform}.\n\nNow send account details in this exact format:\nUsername:Price:Details", None)
        bot.register_next_step_handler(call.message, process_details)

    elif call.data == "show_mm":
        mm_list = "Trusted Middlemen List:\n@wrwww\n@wwwrw\n@is_smaa"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Back", callback_data="back_to_main"))
        safe_edit_text(chat_id, call.message.message_id, mm_list, markup)

    elif call.data.startswith("approve_"):
        target_user_id = int(call.data.split("_")[1])
        post_data = user_pending_posts.get(target_user_id)
        
        if post_data:
            msg = f"Platform: {post_data['platform']}\nUsername: {post_data['username']}\nPrice: {post_data['price']}\nDetails: {post_data['details']}"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Contact Seller", url=f"https://t.me/{call.message.chat.username or 'user'}"))
            
            try:
                bot.send_message(CHANNEL_ID, msg, reply_markup=markup)
                safe_edit_text(chat_id, call.message.message_id, "Post approved and sent to channel.", None)
            except Exception as e:
                bot.send_message(chat_id, "Error: Could not send to channel. Check CHANNEL_ID.")
            
            if target_user_id in user_pending_posts:
                del user_pending_posts[target_user_id]
        else:
            safe_edit_text(chat_id, call.message.message_id, "Error: Post data not found.", None)

    elif call.data == "reject":
        safe_edit_text(chat_id, call.message.message_id, "Post rejected.", None)

def process_details(message):
    try:
        data = message.text.split(":")
        if len(data) != 3:
            raise ValueError
        
        username, price, details = data
        chat_id = message.chat.id
        
        if chat_id in user_pending_posts:
            user_pending_posts[chat_id].update({"username": username, "price": price, "details": details})
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Approve", callback_data=f"approve_{chat_id}"))
            markup.add(types.InlineKeyboardButton("Reject", callback_data="reject"))
            
            admin_msg = f"New Submission from @{message.from_user.username}:\n\nPlatform: {user_pending_posts[chat_id]['platform']}\nUsername: {username}\nPrice: {price}\nDetails: {details}"
            bot.send_message(ADMIN_ID, admin_msg, reply_markup=markup)
            bot.reply_to(message, "Your post has been sent to administration.")
    except ValueError:
        bot.reply_to(message, "Invalid format. Please use: Username:Price:Details")
        bot.register_next_step_handler(message, process_details)

bot.polling()
