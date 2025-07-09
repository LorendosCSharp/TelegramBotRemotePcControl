# TelegramBotRemotePcControl

> Control your PC remotely through a Telegram bot — simple, secure, and efficient.

---

## 🚀 Features

- Send commands to your PC via Telegram
- Control volume, screen, and media playback
- Lightweight and easy to configure

---

## ⚙️ Requirements

Before using this bot, make sure you have the following set up:

1. **Install Python dependencies**

   Install all required Python packages listed in `req.txt` by running:

   ```bash
   pip install -r req.txt

2. **Create a `.env` file**

   The bot requires environment variables for security and configuration. Create a `.env` file in your project root with the following variables:

   ```env
   TOKEN=your_telegram_bot_token_here
   BOT_USERNAME=@your_bot_username_here
   ```

   > **Note:**  
   > - `TOKEN` is your bot token from [Telegram BotFather](https://core.telegram.org/bots#6-botfather).  
   > - `BOT_USERNAME` is your bot’s username (including the `@` symbol).

   For detailed instructions on obtaining these, see the [official Telegram bot tutorial](https://core.telegram.org/bots#3-how-do-i-create-a-bot).

---

## 📦 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/LorendosCSharp/TelegramBotRemotePcControl.git
   cd TelegramBotRemotePcControl
   ```

2. Install dependencies:

   ```bash
   pip install -r req.txt
   ```

3. Set up your `.env` file as described above.
   
4. add your telegrams profiles id to whitelist.json as plain number not a string

5. Run the bot:

   ```bash
   python main.py
   ```

---

## 📚 Usage

Start a chat with your bot on Telegram and use the provided commands/buttons to control your PC remotely.

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Contributions

Contributions, issues, and feature requests are welcome! Feel free to check [issues](https://github.com/yourusername/TelegramBotRemotePcControl/issues).

---


*Happy remote controlling! 🎉*
