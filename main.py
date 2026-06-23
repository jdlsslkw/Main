import telebot
from telebot import types
import os

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

bot = telebot.TeleBot(TOKEN)

# Temporary storage for user posts
user_pending_posts = {}

def get_main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Post New Account", callback_data="select_platform"))
    markup.add(types.InlineKeyboardButton("Trusted Middlemen", callback_data="show_mm"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome to the Trading Bot. Please select an option:", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id

    if call.data == "select_platform":
        markup = types.InlineKeyboardMarkup()
        platforms = ["Instagram", "Snapchat", "TikTok", "Twitter", "Telegram"]
        for p in platforms:
            markup.add(types.InlineKeyboardButton(p, callback_data=f"platform_{p}"))
        bot.edit_message_text("Select the platform:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("platform_"):
        platform = call.data.split("_")[1]
        user_pending_posts[chat_id] = {"platform": platform}
        bot.edit_message_text(f"You selected {platform}.\n\nNow send the account details in this exact format:\nUsername:Price:Details", chat_id, call.message.message_id)
        bot.register_next_step_handler(call.message, process_details)

    elif call.data == "show_mm":
        mm_list = "Trusted Middlemen List:\n@wrwww\n@wwwrw\n@is_smaa"
        bot.edit_message_text(mm_list, chat_id, call.message.message_id, reply_markup=get_main_menu())

    elif call.data.startswith("approve_"):
        user_id = int(call.data.split("_")[1])
        post_data = user_pending_posts.get(user_id)
        
        if post_data:
            # Format the output for the channel
            msg = f"Platform: {post_data['platform']}\nUsername: {post_data['username']}\nPrice: {post_data['price']}\nDetails: {post_data['details']}"
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Contact Seller", url=f"https://t.me/{call.message.chat.username or 'user'}"))
            
            bot.send_message(CHANNEL_ID, msg, reply_markup=markup)
            bot.edit_message_text("Post approved and sent to channel.", chat_id, call.message.message_id)
            del user_pending_posts[user_id]
        else:
            bot.edit_message_text("Error: Post data not found.", chat_id, call.message.message_id)

    elif call.data == "reject":
        bot.edit_message_text("Post rejected.", chat_id, call.message.message_id)

def process_details(message):
    try:
        data = message.text.split(":")
        if len(data) != 3:
            raise ValueError
        
        username, price, details = data
        chat_id = message.chat.id
        
        if chat_id in user_pending_posts:
            user_pending_posts[chat_id].update({
                "username": username,
                "price": price,
                "details": details
            })
            
            # Send to Admin
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Approve", callback_data=f"approve_{chat_id}"))
            markup.add(types.InlineKeyboardButton("Reject", callback_data="reject"))
            
            admin_msg = f"New Submission from @{message.from_user.username}:\n\nPlatform: {user_pending_posts[chat_id]['platform']}\n{message.text}"
            bot.send_message(ADMIN_ID, admin_msg, reply_markup=markup)
            bot.reply_to(message, "Your post has been sent to administration for review.")
            
    except ValueError:
        bot.reply_to(message, "Invalid format. Please use: Username:Price:Details")
        bot.register_next_step_handler(message, process_details)

bot.polling()
