import logging, sys
from telethon import client
import config
import telebot
from telebot import types
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, commandhandler
import asyncio, platform
import telethon
from telegram import message
from telegram.ext.updater import Updater
from telethon import TelegramClient,events
from telethon.tl import functions
import time, os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
TOKEN = config.token
# TOKEN = '1936088901:AAGMu1qIUtYCFGUq_x8WhiglT_3kYZs7oVE'
bot = telebot.TeleBot(TOKEN)

landRange = {"R1": "0-10",'R2':"10-100","R3":">100"}

###########File Creation #################
farmerFile = config.farmerFile

def file_creation(filename, content):
    fileExists = os.path.exists(filename)
    # time.sleep(5)
    
    if (fileExists != True):
        new_file = open(filename,"w")
        new_file.write(content)
        new_file.close()
    
def fileAppend(filename,content):
    fileExists = os.path.exists(filename)
    
    if (fileExists):
        append_f = open(filename,"a+")
        append_f.write("\n" + str(content))
        append_f.close()
    
########### File Creation ends ###########
cpyPrediction = {'Crop Prediction - User'}
def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""

    keyboard = [[InlineKeyboardButton(text = str(text), callback_data=str(text))] for text in cpyPrediction]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose the option:', reply_markup=reply_markup)


def makeKeyboard(userData):
    markup = types.InlineKeyboardMarkup()

    for key, value in userData.items():
        markup.add(types.InlineKeyboardButton(text= value,
                                              callback_data="[" + value ),  #'value': ' + "']"+ "': '" + key
                   # types.InlineKeyboardButton(text=crossIcon,
                   #                            callback_data="['key', '" + key + "']")
                   )

    return markup

def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    
    file_create= file_creation(farmerFile, "farmerFile")
    query = update.callback_query
     
    # CallbackQueries need to be answered, even if no notification to the user is needed
    
    query.answer()
    if (query.data == 'Crop Prediction - User'):

        userData = {"State/City & Crop": "State/City&Crop"}

        bot.send_message(chat_id=query.message.chat.id,
                         text="Enter the Location Details",
                         reply_markup=makeKeyboard(userData=userData),
                         parse_mode='HTML')

        ##### Call back #####
        userquery = update.callback_query
        
        # print(query.data["value"])
        userquery.answer()
        query.edit_message_text(text=f"Selected option: {userquery.data}")

    if (query.data == 'Crop Prediction - Bot'):
        query.edit_message_text(text=f"Selected option: {query.data}")
    api_id = config.api_id
    api_hash = config.api_hash
    session_name = config.session_name
    if (query.data[1:] == 'State/City&Crop'):
        
        query.edit_message_text(text=f"Enter the State, city and crop to sow in the below format \
        \n<<Crop>>\n<<City>>\n<<State>>")
        time.sleep(15)
        
        try:
            async def loop_task():
                client = TelegramClient(session_name,api_id,api_hash)
                await client.start()
                async for message in client.iter_messages(session_name,limit=3):
                    location_value = message.text
                    fileAppend(filename=farmerFile,content=location_value)
                    
                return location_value
                
            def coro_function():
                asyncio.run(loop_task())
            import threading
            threading.Thread(target=coro_function).start()        
            
        except TypeError as TE:
            fileAppend(filename=farmerFile,content=TE)
        except RuntimeError as RE:
            fileAppend(filename=farmerFile,content=RE)
    
        time.sleep(5)
        QuarterData = {"Season": "Season"}

        bot.send_message(chat_id=query.message.chat.id,
                         text="Please choose the Season to sow:",
                         reply_markup=makeKeyboard(userData=QuarterData),
                         parse_mode='HTML')
    if (query.data[1:] == 'Season'):
        query.edit_message_text(text=f"Range: {query.data[1:]}")
        SeasonRange = {"WholeYear":"Jan-Dec","Kharif":"June-Oct","Rabi":"Nov-Apr","Autumn":"Sep-Nov","Summer":"Apr-June","Winter":"Dec-Jan"}
        bot.send_message(chat_id=query.message.chat.id,
                         text="Please choose the Season:",
                         reply_markup=makeKeyboard(userData=SeasonRange),
                         parse_mode='HTML')
    if (query.data[1:] in ('Jan-Dec','Apr-June','June-Oct','Sep-Nov','Dec-Jan','Nov-Apr')):
        query.edit_message_text(text=f"SeasonRange: {query.data[1:]}")
        Seasonrange = query.data[1:]
        fileAppend(filename=farmerFile,content=Seasonrange)
        
        time.sleep(3)
        file_creation(config.farmerIndicator,"Welcome")
        bot.send_message(chat_id=query.message.chat.id,
                         text="Please wait FarmerBot is working on your request....",
                         reply_markup=None,
                         parse_mode=None)
def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("Use /start to test this bot.")

def stop_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("Use /stop to stop this bot.")

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
    
if __name__ == '__main__':
    main()