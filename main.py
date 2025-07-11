from dotenv import load_dotenv
import os
import json
import tempfile
import asyncio
from typing import Final

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
import keyboard as kb
import mss
import mss.tools

# Load environment variables
load_dotenv()
TOKEN: Final = os.getenv('TOKEN')
BOT_USERNAME: Final = os.getenv('BOT_USERNAME')

#region Constants
MOVIE_MENU_NAME = "\u2605 \u2605 \u2605   M  O  V  I  E   \u2605 \u2605 \u2605"
PC_MENU_NAME = "\u2605 \u2605 \u2605   PC   \u2605 \u2605 \u2605"

# Movie mode buttons
PAUSE_UNPAUSE_BUTTON = "\u23EF\uFE0F"
VOLUME_UP_BUTTON = "\U0001F50A"
VOLUME_DOWN_BUTTON = "\U0001F509"
VOLUME_MUTE_BUTTON = "\U0001F507"
FULL_UNFULL_SCREEN_BUTTON = "\U0001F4FA"

MOVIE_INLINEKEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(PAUSE_UNPAUSE_BUTTON, callback_data=PAUSE_UNPAUSE_BUTTON),
        InlineKeyboardButton(FULL_UNFULL_SCREEN_BUTTON, callback_data=FULL_UNFULL_SCREEN_BUTTON)
    ],
    [
        InlineKeyboardButton(VOLUME_UP_BUTTON, callback_data=VOLUME_UP_BUTTON),
        InlineKeyboardButton(VOLUME_DOWN_BUTTON, callback_data=VOLUME_DOWN_BUTTON),
        InlineKeyboardButton(VOLUME_MUTE_BUTTON, callback_data=VOLUME_MUTE_BUTTON)
    ]
])

# PC mode buttons
SYSTEM_VOLUME_UP_BUTTON = "\U0001F50A"
SYSTEM_VOLUME_DOWN_BUTTON = "\U0001F509"
SYSTEM_VOLUME_MUTE_BUTTON = "\U0001F507"
SYSTEM_SHUTDOWN_BUTTON = "\u274C\u26A1\u274C"
SYSTEM_REBOOT_BUTTON = "\U0001F501"
SYSTEM_LOCK_BUTTON = "\U0001F512"
GET_SCREENSHOT_BUTTON = "\U0001F4FA"

PC_INLINEKEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(SYSTEM_VOLUME_UP_BUTTON, callback_data=SYSTEM_VOLUME_UP_BUTTON),
        InlineKeyboardButton(SYSTEM_VOLUME_DOWN_BUTTON, callback_data=SYSTEM_VOLUME_DOWN_BUTTON),
        InlineKeyboardButton(SYSTEM_VOLUME_MUTE_BUTTON, callback_data=SYSTEM_VOLUME_MUTE_BUTTON)
    ],
    [
        InlineKeyboardButton(SYSTEM_SHUTDOWN_BUTTON, callback_data=SYSTEM_SHUTDOWN_BUTTON),
        InlineKeyboardButton(SYSTEM_REBOOT_BUTTON, callback_data=SYSTEM_REBOOT_BUTTON)
    ],
    [InlineKeyboardButton(SYSTEM_LOCK_BUTTON, callback_data=SYSTEM_LOCK_BUTTON)],
    [InlineKeyboardButton(GET_SCREENSHOT_BUTTON, callback_data=GET_SCREENSHOT_BUTTON)]
])
#endregion

#region Commands
async def movie_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MOVIE_MENU_NAME, reply_markup=MOVIE_INLINEKEYBOARD)

async def pc_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(PC_MENU_NAME, reply_markup=PC_INLINEKEYBOARD)

async def killswitch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\u274C Bot shutting down")
    os._exit(0)

#endregion

#region Message Handlers
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_user_whitelisted(update.message.from_user.id):
        await update.message.reply_text("You are not in whitelist")
        return

    await update.message.reply_text("\u2705 Use /movie or /pc to get started")

async def handle_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    menu_type = query.message.text

    if not is_user_whitelisted(query.from_user.id):
        await query.answer("You are not in whitelist", show_alert=True)
        return

    if menu_type == MOVIE_MENU_NAME:
        key_map = {
            VOLUME_DOWN_BUTTON: 'down',
            VOLUME_UP_BUTTON: 'up',
            VOLUME_MUTE_BUTTON: 'm',
            FULL_UNFULL_SCREEN_BUTTON: 'f',
            PAUSE_UNPAUSE_BUTTON: 'space'
        }
        if data in key_map:
            kb.press_and_release(key_map[data])

    elif menu_type == PC_MENU_NAME:
        if data == SYSTEM_VOLUME_DOWN_BUTTON:
            kb.press_and_release('volume down')
        elif data == SYSTEM_VOLUME_UP_BUTTON:
            kb.press_and_release('volume up')
        elif data == SYSTEM_VOLUME_MUTE_BUTTON:
            kb.press_and_release('volume mute')
        elif data == SYSTEM_SHUTDOWN_BUTTON:
            os.system("shutdown -t 0 -s -f")
        elif data == SYSTEM_REBOOT_BUTTON:
            os.system("shutdown -t 0 -r -f")
        elif data == SYSTEM_LOCK_BUTTON:
            os.system('rundll32.exe user32.dll,LockWorkStation')
        elif data == GET_SCREENSHOT_BUTTON:
            await capture_each_monitor_and_send(update, context)

#endregion

#region Screenshot
async def capture_each_monitor_and_send(update, context):
    with mss.mss() as sct:
        for i, monitor in enumerate(sct.monitors[1:], start=1):
            with tempfile.NamedTemporaryFile(suffix=f'_monitor{i}.png', delete=False) as tmpfile:
                temp_path = tmpfile.name

            try:
                shot = sct.grab(monitor)
                mss.tools.to_png(shot.rgb, shot.size, output=temp_path)

                with open(temp_path, 'rb') as f:
                    await context.bot.send_photo(update.effective_chat.id, photo=f)

            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
#endregion

#region Utilities
def is_user_whitelisted(userid: int, path='whitelist.json') -> bool:
    with open(path, 'r') as f:
        whitelist = set(json.load(f))
    return userid in whitelist

async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
#endregion

#region Main
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("movie", movie_mode_command))
    app.add_handler(CommandHandler("pc", pc_mode_command))
    app.add_handler(CommandHandler("kill", killswitch_command))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(handle_keyboard))

    app.add_error_handler(handle_error)

    print("Bot running...")
    app.run_polling(poll_interval=1)
#endregion
