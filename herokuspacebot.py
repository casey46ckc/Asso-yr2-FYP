import configparser
import logging
import os
from readjson import replace_AbbrName, read_multiwords_json, read_json
from copy import deepcopy
import telegram


import nltk
import nltk.tag, nltk.data
nltk.download('stopwords')

from telegram import ReplyKeyboardMarkup,ReplyKeyboardRemove, Update
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
from nlp.olami import Olami
from nltk.tokenize import MWETokenizer, TweetTokenizer, word_tokenize
from nltk.corpus import stopwords

from schedule.schedule import TheSemesterTimeSchedule, collect_result_V1, readClSchedule, codeValidity, getRank

# initialize the greeting message for /start command
start_message = []

# initialize the help message for /help command
help_message = ['You may call 3762 2222 or email to ccad@hkuspace.hku.hk for further enquiries.']

# initial the reply keyboard from start
reply_kb_start = ReplyKeyboardMarkup([['Guideline'],['Help']], one_time_keyboard=True)

# initial the reply keyboard for university choice
reply_kb_university = ReplyKeyboardMarkup([
    ["City University of Hong Kong"],
    ["Hong Kong Baptist University"],
    ["Lingnan University"],
    ["The Chinese University of Hong Kong"],
    ["The Education University of Hong Kong"],
    ["The Hong Kong Polytechnic University"],
    ["The Hong Kong University of Science and Technology"],
    ["The University of Hong Kong"],
    ["Hang Seng University of Hong Kong"],
    ["Hong Kong Shue Yan University"],
    ["The Open University of Hong Kong"],
    ["Others"]],
    one_time_keyboard=True)



# reply_kb_example = ReplyKeyboardMarkup([['Where is the library?'],['Tell me the contact of KEC']], one_time_keyboard=True)

# initial the nltk parts
default_tagger = nltk.tag.DefaultTagger('NN')
model = read_json('json/models.json')
tl_MWs = read_multiwords_json('json/multiwords.json')

tags_dict = {}

tagger = nltk.tag.UnigramTagger(model=model, backoff=default_tagger)
tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
mwtknzr = MWETokenizer(tl_MWs)
stop_words = set(stopwords.words('english'))


# initialize the list of information for class schedule
clList = readClSchedule('schedule/MTT_2021S2_Custom.xls')

def createKeyBoardLayout(btnStringList: list)->ReplyKeyboardMarkup:
    for btsString in btnStringList:
        if isinstance(btsString, list):
            if len(btsString) == 1:
                for tmp_str in btsString:
                    if isinstance(tmp_str, str):
                        pass
                    else:
                        return ReplyKeyboardMarkup([[""]], one_time_keyboard=True)
            else:
                return ReplyKeyboardMarkup([[""]], one_time_keyboard=True)
        else:
            return ReplyKeyboardMarkup([[""]], one_time_keyboard=True)
    return ReplyKeyboardMarkup(btnStringList, one_time_keyboard=True)





def reply_handler(update: Update, context: CallbackContext):
    text = update.message.text
    # nltk part, lowercase for convienence
    textToken = text.lower()
    tkn0 = tknzr.tokenize(textToken)
    # print(f'tkn0[{type(tkn0)}]: ', tkn0)
    mwtkn0 = mwtknzr.tokenize(tkn0)
    # print(f'mwtkn0[{type(mwtkn0)}]: ', mwtkn0)
    filtered_tkn0 = [w for w in mwtkn0 if not w in stop_words]
    # print(f'filtered_tkn[{type(filtered_tkn0)}]: ', filtered_tkn0)
    filtered_tkn0Tag = tagger.tag(filtered_tkn0)
    # print(f'filtered_tkn0Tag[{type(filtered_tkn0Tag)}]: ', filtered_tkn0Tag)

    # shorten the message
    text = replace_AbbrName(textToken)
    print("Text after abbr: " + text)
    """Reply message."""
    user_id = update.message.from_user.id
    global tags_dict
    print("tags_dict:", tags_dict, "length:", len(tags_dict))

    if str(user_id) in tags_dict:
        reply = Olami().nli(text, user_id, tags_dict[str(user_id)])
    else:
        reply = Olami().nli(text, user_id)

    if reply['status'] == "True":
        if str(user_id) in tags_dict:
            del tags_dict[str(user_id)]
    elif reply['status'] == "False":
        logger.info(f'reply:\n {reply}')
        tags_dict[str(user_id)] = {}
        tags_dict[str(user_id)]['tag'] = deepcopy(reply['tag'])
        if 'slotsvalue' in reply:
            logger.info(f'returned slotsvalue: {reply["slotsvalue"]}')
            tags_dict[str(user_id)]['slotsvalue'] = reply['slotsvalue']

    print(reply['response'])
    if 'keyBoardLayout' in reply:
        if len(reply['keyBoardLayout']) > 0:
            print("keyBoardLayout triggered")
            update.message.reply_text('\n'.join(reply['response']), reply_markup=createKeyBoardLayout(reply['keyBoardLayout']))
        else:
            update.message.reply_text('\n'.join(reply['response']), reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('\n'.join(reply['response']), reply_markup=ReplyKeyboardRemove())

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
                    update.message.reply_text(f"Rank #{i + 1}:\n" + result_sorted[i].displayInfo(), parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text("Usage:\n" + "\t/spacedule <Class Code><Class No>(<Class No> can be omitted) * N\n" +
        "To find the most optimized classes for add/drop/swap")
        update.message.reply_text("e.g. /spacedule CCCH4003 CCCU4041 CCEN4005 CCIT4033CL03 CCIT4059 CCIT4080CL07")
        update.message.reply_text('\n'.join([
            "Result will be ordered by total marks and the marking scheme is as followed:",
            "+ 10 marks for each day of day-off, including saturday",
            "-  3 marks for each day of early morning lessons or late evening lessons",
            "-  2 marks for the time gap between two lessons within one day is greater than 3 hours",
            " ***Only top 10 results will be display through the message***"]))

def error_handler(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text("Please be patience. It require more time for processing")


if __name__ == "__main__":
    # Load data from config.ini file
    config = configparser.ConfigParser()
    config.read('config.ini')    

    # Set these variable to the appropriate values
    TOKEN = config['TELEGRAM']['ACCESS_TOKEN']
    NAME = config['HEROKU']['APP_NAME']

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Add handlers
    dp.add_handler(CommandHandler('start', start_handler))
    dp.add_handler(CommandHandler('help', help_handler))
    dp.add_handler(CommandHandler('spacedule', clSchedule_handler))
    dp.add_error_handler(error_handler)
    dp.add_handler(MessageHandler(Filters.text, reply_handler))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    updater.idle()