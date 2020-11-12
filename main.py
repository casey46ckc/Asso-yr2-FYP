import configparser
import logging

import telegram
from flask import Flask, request
from telegram import ReplyKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from nlp.olami import Olami

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=(config['TELEGRAM']['ACCESS_TOKEN']))


# initialize the greeting message for /start command
start_message = []

# initialize the help message for /help command
help_message = ['Where is <facility name in KEC>?', 'Which floor <facility name in KEC> is?', 'Tell me the contact of <block name of HKUSpace>?']

# initial the reply keyboard from start
reply_kb_start = ReplyKeyboardMarkup([['Where is the library?'],['Tell me the contact of KEC']], one_time_keyboard=True)


@app.route('/hook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'


def reply_handler(bot, update):
    """Reply message."""
    text = update.message.text
    user_id = update.message.from_user.id
    reply = Olami().nli(text, user_id)
    update.message.reply_text(reply)

def start_handler(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Greetings! Welcome to spacebot", reply_markup=reply_kb_start)

def help_handler(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Commands now supported:\n" + "\n".join(help_message),reply_markup=reply_kb_start)

def error_handler(bot, update, error):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, error)
    update.message.reply_text("Please be patience. It require more time for processing")


# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.

dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('help', help_handler))
dispatcher.add_error_handler(error_handler)
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)
