from dotenv import load_dotenv
import os
from typing import Final
import json
from telegram import Update,InlineKeyboardMarkup,InlineKeyboardButton
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes,CallbackQueryHandler
from pynput.keyboard import Controller, Key

#Gets essential vars from env file ; NEEDS TO CONTAIN THESE VARS
load_dotenv()
TOKEN:Final = os.getenv('TOKEN')
BOT_USERNAME:Final = os.getenv('BOT_USERNAME')

kb = Controller()

#Variable for Movie Mode
MOVIE_MENU_NAME="★ ★ ★   M  O  V  I  E   ★ ★ ★"

#buttons
PAUSE_UNPAUSE_BUTTON="⏯️"
VOLUME_UP_BUTTON="🔊"
VOLUME_DOWN_BUTTON="🔈"
VOLUME_MUTE_BUTTON="🔇"
FULL_UNFULL_SCREEN_BUTTON="📺"

#Keyboard with the buttons
MOVIE_INLINEKEYBOARD= InlineKeyboardMarkup([
    [InlineKeyboardButton(PAUSE_UNPAUSE_BUTTON, callback_data=PAUSE_UNPAUSE_BUTTON),InlineKeyboardButton(FULL_UNFULL_SCREEN_BUTTON, callback_data=FULL_UNFULL_SCREEN_BUTTON)],
    [InlineKeyboardButton(VOLUME_UP_BUTTON, callback_data=VOLUME_UP_BUTTON),InlineKeyboardButton(VOLUME_DOWN_BUTTON, callback_data=VOLUME_DOWN_BUTTON),InlineKeyboardButton(VOLUME_MUTE_BUTTON, callback_data=VOLUME_MUTE_BUTTON)]
])

async def movie_mode_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MOVIE_MENU_NAME,parse_mode="HTML",reply_markup=MOVIE_INLINEKEYBOARD)

def handle_respone(text:str)-> str:

    processed:str=text.lower()

    if "hello" in processed:
        return "no helloski to you"
    
    return "beep boop"

async def handle_message(update:Update,context:ContextTypes.DEFAULT_TYPE):

    message_type:str= update.message.chat.type
    text:str = update.message.text
    response:str=""
    if not is_user_whitelisted(update.message.from_user.id):
        await update.message.reply_text("You are not in whitelist")
        return
    
    if message_type =="group":
        if BOT_USERNAME in text:
            new_text:str = text.replace(BOT_USERNAME,"").strip()
            response = handle_respone(new_text)
        else:
            return
    else:
        response = handle_respone(text)

    await update.message.reply_text(response)

async def handle_error(update:Update,context:ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

async def handle_keyboard(update:Update,context:ContextTypes.DEFAULT_TYPE):
    data:str = update.callback_query.data

    if not is_user_whitelisted(update.callback_query.from_user.id):
        await update.callback_query.answer("You are not in whitelist",show_alert=True)
        return
    
    if update.callback_query.message.text==MOVIE_MENU_NAME:
        if data == VOLUME_DOWN_BUTTON:
            press_and_release(Key.media_volume_down)
        elif data == VOLUME_UP_BUTTON:
            press_and_release(Key.media_volume_up)
        elif data == VOLUME_MUTE_BUTTON:
            press_and_release(Key.media_volume_mute)
        elif data == FULL_UNFULL_SCREEN_BUTTON:
            press_and_release('f')
        elif data==PAUSE_UNPAUSE_BUTTON:
            press_and_release(Key.space)
        else :
            print("incorrect data")

    await update.callback_query.answer()

#help methods
def is_user_whitelisted(userid: str, path='whitelist.json') -> bool:
    with open(path, 'r') as f:
        json_unpacked = json.load(f)
        whitelist = set(json_unpacked)
    return userid in whitelist

def press_and_release(key):
    kb.press(key)
    kb.release(key)

if __name__=="__main__":
    print("starting bot ..")

    app = Application.builder().token(TOKEN).build()

    #Commands
    app.add_handler(CommandHandler("movie",movie_mode_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT,handle_message))

    #Callbacks
    app.add_handler(CallbackQueryHandler(handle_keyboard))

    #Errors
    app.add_error_handler(handle_error)

    app.run_polling(poll_interval=1)