import configparser
import logging

import telegram

from flask import Flask, request
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
from nlp.olami import Olami
from readjson import replace_AbbrName
from schedule.schedule import TheSemesterTimeSchedule, collect_result_V1, readClSchedule, codeValidity, getRank

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
reply_kb_start = ReplyKeyboardMarkup([['Guideline'],['Help']], one_time_keyboard=True)
# reply_kb_example = ReplyKeyboardMarkup([['Where is the library?'],['Tell me the contact of KEC']], one_time_keyboard=True)

# initialize the list of information for class schedule
clList = readClSchedule('schedule/MTT_2021S2_Custom.xls')


@app.route('/hook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

# TODO: handle enquiryinfo for further questions by adding one more parameter pass the .nli() function
def reply_handler(update: Update, context: CallbackContext):
    # shorten the message
    text = update.message.text
    text = replace_AbbrName(text)

    """Reply message."""
    user_id = update.message.from_user.id
    reply = Olami().nli(text, user_id)
    update.message.reply_text(reply)

def start_handler(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Greetings! Welcome to spacebot", reply_markup=reply_kb_start)

def help_handler(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Commands now supported:\n" + "\n".join(help_message), reply_markup=reply_kb_start)

def clSchedule_handler(update: Update, context: CallbackContext):
    """Send a message when the command /spacedule is issued."""
    if len(context.args) > 0:
        clSList = []
        resultList = []
        depth = len(context.args)
        errFlag = False
        for i in range(depth):
            tmpList = codeValidity(clList, context.args[i])
            if(len(tmpList) != 0):
                clSList.append(tmpList)
            else:
                update.message.reply_text("Error: incorrect course code input. Please try again")
                errFlag = True
                break
        if errFlag != True:
            collect_result_V1(resultList, depth, 0, *clSList)
            result_sorted = sorted(resultList, key=getRank, reverse=True)
            for i in range(len(result_sorted)):
                if(i < 10):
                    update.message.reply_text(result_sorted[i].displayInfo())
    else:
        update.message.reply_text("Usage:\n" + "\t/spacedule <Class Code>(<Class No>) * N\n" +
        "To find the most optimized time table for add/drop/swap")
        update.message.reply_text("e.g. /spacedule CCCH4003 CCCU4041 CCEN4005 CCIT4033CL03 CCIT4059 CCIT4080CL07")
        update.message.reply_text("Result will be ordered by ranking and the constraints of ranking are as follow:\n"+
        "+ 10 marks for each day of day-off, including saturday\n"+
        "-  3 marks for each day of early morning lessons or late evening lessons\n"+
        "-  2 marks for the time gap between two lessons within one day is greater than 3 hours\n"
        "\n **Only top 10 results will be display through the message\n")

def error_handler(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text("Please be patience. It require more time for processing")


# New a dispatcher for bot
dispatcher = Dispatcher(bot, None, use_context=True)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.

dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('help', help_handler))
dispatcher.add_handler(CommandHandler('spacedule', clSchedule_handler))
dispatcher.add_error_handler(error_handler)
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)
