from dotenv import load_dotenv
import os
import json
from enum import Enum
import tempfile
from typing import Final

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton, CallbackQuery, WebAppInfo,
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
import pyautogui

class BUTTONS_ENUM(str, Enum):
    ##Buttons for the PC Mode
    SYSTEM_VOLUME_UP_BUTTON = "S🔊"
    SYSTEM_VOLUME_DOWN_BUTTON = "S🔈"
    SYSTEM_VOLUME_MUTE_BUTTON = "S🔇"
    SYSTEM_SHUTDOWN_BUTTON = "❌⚡❌"
    SYSTEM_REBOOT_BUTTON = "🔄"
    SYSTEM_LOCK_BUTTON = "🔒"
    GET_SCREENSHOT_BUTTON = "📺"

    ##Buttons for the Movie Mode
    PAUSE_UNPAUSE_BUTTON = "⏯️"
    VOLUME_UP_BUTTON = "🔊"
    VOLUME_DOWN_BUTTON = "🔈"
    VOLUME_MUTE_BUTTON = "🔇"
    FULL_UNFULL_SCREEN_BUTTON = "⛶"
    SKIP_FORWARD_BUTTON = "⏩"
    SKIP_BACKWARD_BUTTON = "⏪"

    ##Different Buttons
    CONFIRM_BUTTON = "✅"
    REJECT_BUTTON = "❌"

    ##Mouse
    MOVE_UP = "⬆️"
    MOVE_DOWN = "⬇️"
    MOVE_LEFT = "⬅️"
    MOVE_RIGHT = "➡️"
    LEFT_CLICK = "🖱️ L"
    RIGHT_CLICK = "🖱️ R"


# Load environment variables
load_dotenv()
TOKEN: Final = os.getenv('TOKEN')
BOT_USERNAME: Final = os.getenv('BOT_USERNAME')

# region Constants
MOVIE_MENU_NAME = "★ ★ ★   M  O  V  I  E   ★ ★ ★"
PC_MENU_NAME = "★ ★ ★   PC   ★ ★ ★"
CURRENT_MENU = ""
CURRENT_MARKUP = None

MOUSE_MOVE_INCREMENT=20

MOVIE_INLINEKEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(BUTTONS_ENUM.SKIP_BACKWARD_BUTTON, callback_data=BUTTONS_ENUM.SKIP_BACKWARD_BUTTON),
        InlineKeyboardButton(BUTTONS_ENUM.PAUSE_UNPAUSE_BUTTON, callback_data=BUTTONS_ENUM.PAUSE_UNPAUSE_BUTTON),
        InlineKeyboardButton(BUTTONS_ENUM.SKIP_FORWARD_BUTTON, callback_data=BUTTONS_ENUM.SKIP_FORWARD_BUTTON)
    ],
    [
        InlineKeyboardButton(BUTTONS_ENUM.FULL_UNFULL_SCREEN_BUTTON,
                             callback_data=BUTTONS_ENUM.FULL_UNFULL_SCREEN_BUTTON),
        InlineKeyboardButton(BUTTONS_ENUM.VOLUME_UP_BUTTON, callback_data=BUTTONS_ENUM.VOLUME_UP_BUTTON),
        InlineKeyboardButton(BUTTONS_ENUM.VOLUME_DOWN_BUTTON, callback_data=BUTTONS_ENUM.VOLUME_DOWN_BUTTON),
        InlineKeyboardButton(BUTTONS_ENUM.VOLUME_MUTE_BUTTON, callback_data=BUTTONS_ENUM.VOLUME_MUTE_BUTTON)
    ]
])

# PC mode buttons


PC_INLINEKEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(BUTTONS_ENUM.SYSTEM_VOLUME_UP_BUTTON, callback_data=BUTTONS_ENUM.SYSTEM_VOLUME_UP_BUTTON),
        InlineKeyboardButton(BUTTONS_ENUM.SYSTEM_VOLUME_DOWN_BUTTON,
                             callback_data=BUTTONS_ENUM.SYSTEM_VOLUME_DOWN_BUTTON),
        InlineKeyboardButton(BUTTONS_ENUM.SYSTEM_VOLUME_MUTE_BUTTON,
                             callback_data=BUTTONS_ENUM.SYSTEM_VOLUME_MUTE_BUTTON)
    ],
    [
        InlineKeyboardButton(BUTTONS_ENUM.SYSTEM_SHUTDOWN_BUTTON, callback_data=BUTTONS_ENUM.SYSTEM_SHUTDOWN_BUTTON),
        InlineKeyboardButton(BUTTONS_ENUM.SYSTEM_REBOOT_BUTTON, callback_data=BUTTONS_ENUM.SYSTEM_REBOOT_BUTTON)
    ],
    [InlineKeyboardButton(BUTTONS_ENUM.SYSTEM_LOCK_BUTTON, callback_data=BUTTONS_ENUM.SYSTEM_LOCK_BUTTON)],
    [InlineKeyboardButton(BUTTONS_ENUM.GET_SCREENSHOT_BUTTON, callback_data=BUTTONS_ENUM.GET_SCREENSHOT_BUTTON)]
])

MOUSE_INLINEKEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(BUTTONS_ENUM.MOVE_UP, callback_data=BUTTONS_ENUM.MOVE_UP),
        InlineKeyboardButton(BUTTONS_ENUM.MOVE_LEFT, callback_data=BUTTONS_ENUM.MOVE_LEFT),
        InlineKeyboardButton(BUTTONS_ENUM.MOVE_RIGHT, callback_data=BUTTONS_ENUM.MOVE_RIGHT),
        InlineKeyboardButton(BUTTONS_ENUM.MOVE_DOWN, callback_data=BUTTONS_ENUM.MOVE_DOWN)

    ],
    [
        InlineKeyboardButton(BUTTONS_ENUM.RIGHT_CLICK, callback_data=BUTTONS_ENUM.RIGHT_CLICK),
        InlineKeyboardButton(BUTTONS_ENUM.LEFT_CLICK, callback_data=BUTTONS_ENUM.LEFT_CLICK),
    ],
])
CONFIRMATION_INLINEKEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton(BUTTONS_ENUM.CONFIRM_BUTTON, callback_data=BUTTONS_ENUM.CONFIRM_BUTTON)],
    [InlineKeyboardButton(BUTTONS_ENUM.REJECT_BUTTON, callback_data=BUTTONS_ENUM.REJECT_BUTTON)]
])


# endregion

# region Commands
async def movie_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MOVIE_MENU_NAME, reply_markup=MOVIE_INLINEKEYBOARD)


async def pc_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(PC_MENU_NAME, reply_markup=PC_INLINEKEYBOARD)


async def mouse_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MOUSE_MOVE_INCREMENT
    MOUSE_MOVE_INCREMENT=int(context.args[0])

    await update.message.reply_text(PC_MENU_NAME, reply_markup=MOUSE_INLINEKEYBOARD)


async def killswitch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\u274C Bot shutting down")
    os._exit(0)


# endregion

# region Message Handlers
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_user_whitelisted(update.message.from_user.id):
        await update.message.reply_text("You are not in whitelist")
        return

    await update.message.reply_text("\u2705 Use /movie or /pc to get started")


async def handle_mouse(data, context: ContextTypes.DEFAULT_TYPE):
    global MOUSE_MOVE_INCREMENT

    match data:
        case BUTTONS_ENUM.MOVE_UP:
            pyautogui.moveRel(0, -MOUSE_MOVE_INCREMENT)
        case BUTTONS_ENUM.MOVE_DOWN:
            pyautogui.moveRel(0, MOUSE_MOVE_INCREMENT)
        case BUTTONS_ENUM.MOVE_LEFT:
            pyautogui.moveRel(-MOUSE_MOVE_INCREMENT, 0)
        case BUTTONS_ENUM.MOVE_RIGHT:
            pyautogui.moveRel(MOUSE_MOVE_INCREMENT, 0)
        case BUTTONS_ENUM.LEFT_CLICK:
            pyautogui.click(button='left')
        case BUTTONS_ENUM.RIGHT_CLICK:
            pyautogui.click(button='right')

async def handle_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if not is_user_whitelisted(query.from_user.id):
        await query.answer("You are not in whitelist", show_alert=True)
        return

    await handle_mouse(data,context)
    await handle_confirmation(update, context, data)
    await execute_modes(update, context, query, data)


async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, function, title):
    query = update.callback_query
    context.user_data["pending_function"] = function
    await query.edit_message_text(title, reply_markup=CONFIRMATION_INLINEKEYBOARD)
    await query.answer()


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, data):
    query = update.callback_query
    await query.answer()

    func = context.user_data.get("pending_function")
    global CURRENT_MENU
    global CURRENT_MARKUP
    if data == BUTTONS_ENUM.CONFIRM_BUTTON:
        func()
        await query.edit_message_text(CURRENT_MENU, reply_markup=CURRENT_MARKUP)
        context.user_data["pending_function"] = None
    elif data == BUTTONS_ENUM.REJECT_BUTTON:
        await query.edit_message_text(CURRENT_MENU, reply_markup=CURRENT_MARKUP)
        context.user_data["pending_function"] = None


async def execute_modes(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQuery, data):
    global CURRENT_MARKUP
    global CURRENT_MENU

    match data:
        ##PC Mode Logic
        case BUTTONS_ENUM.SYSTEM_VOLUME_DOWN_BUTTON:
            kb.press_and_release('volume down')
        case BUTTONS_ENUM.SYSTEM_VOLUME_UP_BUTTON:
            kb.press_and_release('volume up')
        case BUTTONS_ENUM.SYSTEM_VOLUME_MUTE_BUTTON:
            kb.press_and_release('volume mute')
        case BUTTONS_ENUM.SYSTEM_SHUTDOWN_BUTTON:
            CURRENT_MENU = PC_MENU_NAME
            CURRENT_MARKUP = PC_INLINEKEYBOARD
            await show_confirmation(update, context, lambda: os.system("shutdown -t 0 -s -f"), "Shut system down?")
        case BUTTONS_ENUM.SYSTEM_REBOOT_BUTTON:
            CURRENT_MENU = PC_MENU_NAME
            CURRENT_MARKUP = PC_INLINEKEYBOARD
            await show_confirmation(update, context, lambda: os.system("shutdown -t 0 -r -f"), "Reboot system?")
        case BUTTONS_ENUM.SYSTEM_LOCK_BUTTON:
            CURRENT_MENU = PC_MENU_NAME
            CURRENT_MARKUP = PC_INLINEKEYBOARD
            await show_confirmation(update, context, lambda: os.system('rundll32.exe user32.dll,LockWorkStation'),
                                    "Lock screen?")
        case BUTTONS_ENUM.GET_SCREENSHOT_BUTTON:
            await capture_each_monitor_and_send(update, context)
            ##Movie Mode Logic
        case BUTTONS_ENUM.VOLUME_DOWN_BUTTON:
            kb.press_and_release('down')
        case BUTTONS_ENUM.VOLUME_UP_BUTTON:
            (
                kb.press_and_release('up'))
        case BUTTONS_ENUM.VOLUME_MUTE_BUTTON:
            (
                kb.press_and_release('m'))
        case BUTTONS_ENUM.FULL_UNFULL_SCREEN_BUTTON:
            (
                kb.press_and_release('f'))
        case BUTTONS_ENUM.PAUSE_UNPAUSE_BUTTON:
            (
                kb.press_and_release('space'))
        case BUTTONS_ENUM.SKIP_FORWARD_BUTTON:
            kb.press_and_release("right")
        case BUTTONS_ENUM.SKIP_BACKWARD_BUTTON:
            kb.press_and_release("left")


# endregion

# region Screenshot
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


# endregion

# region Utilities
def is_user_whitelisted(userid: int, path='whitelist.json') -> bool:
    with open(path, 'r') as f:
        whitelist = set(json.load(f))
    return userid in whitelist


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


# endregion

# region Main
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("movie", movie_mode_command))
    app.add_handler(CommandHandler("pc", pc_mode_command))
    app.add_handler(CommandHandler("mouse", mouse_mode_command))
    app.add_handler(CommandHandler("kill", killswitch_command))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(handle_keyboard))

    app.add_error_handler(handle_error)

    print("Bot running...")
    app.run_polling(poll_interval=0.1)
# endregion
