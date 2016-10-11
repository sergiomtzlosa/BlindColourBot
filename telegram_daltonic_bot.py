#!/usr/bin/python

# Install Telebot: git clone https://github.com/eternnoir/pyTelegramBotAPI.git
# Install a lot of things: sudo apt-get install libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk
# Install Pillow: pip install Pillow
# Install Matplotlib: sudo apt-get install python-matplotlib
# Install scipy: sudo apt-get install python-scipy
# Install numpy >= 1.9.0: pip install numpy

# Create two folders inside SAVE_PATH:
# mkdir SAVE_PATH/incoming_images
# mkdir SAVE_PATH/outcoming_images

# /setprivacy to false on @BotFather to let this bot read all messages from group or conversation

import telebot
from datetime import datetime
from telebot import types
import logging
import time
import requests
import subprocess
import os
import sys
import shutil
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

BASE_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

TOKEN = "285289285:AAGyLiGG3NNBVWp28xPwtv0EhOT3WMKD95Q"

SAVE_PATH = "/media/HDD2/telegram_bot/images"

bot = telebot.TeleBot(TOKEN)

#logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

user_dict = {} 

def send_message(cid, text):
    bot.send_message(cid, text)

def send_document(cid, document):
    bot.send_document(cid, document)

def send_photo(cid, photo_path):
   photo = open(photo_path, 'rb') 
   bot.send_photo(cid, photo)

def reply_to(message, text):
    bot.reply_to(message, text)

def answer_inline_query(inline_query_id, array_types):
    bot.answer_inline_query(inline_query_id, array_types)

def download_image(file_id):
    file_info = bot.get_file(file_id)
    photo_url = "https://api.telegram.org/file/bot{0}/{1}".format(TOKEN, file_info.file_path)
    file = requests.get(photo_url, stream=True)
    return file

def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)

def current_time():
    date = datetime.now()
    final_date = date.strftime('%Y-%m-%d_%H:%M:%S')
    return str(final_date)

def system_call(command):
    p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    out = p.stdout.read()
    out = out.replace("\n", "")
    return out

def save_file(file):
    random_string = system_call("/usr/bin/head /dev/urandom | tr -dc A-Za-z0-9 | /usr/bin/head -c 5 | xargs echo").lower()
    final_image_path = SAVE_PATH + '/incoming_images/new_file_' + current_time() + "_" + random_string + '.png'
    touch(final_image_path)
    with open(final_image_path, 'wb') as new_file:
         shutil.copyfileobj(file.raw, new_file)
    return final_image_path

def adjust_image(image_in, image_out, blindness_type):
    blind = "d"
    if blindness_type == "protanopia":
       blind = "p"
    if blindness_type == "tritanopia":
       blind = "t"
    os.system("/usr/bin/python " + BASE_PATH + "/daltonize/daltonize.py -d -t " + blind + " " + image_in + " " + image_out)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    reply_to(message, "This is a daltonic bot, it adjusts image color palette for color blindness.\nSend an image to adjust colour for blind colour people. Send only jpg or png files.")

@bot.message_handler(func=lambda message: True, content_types=['photo'])
def echo_all(message):
    process_start_daltonize(message)

def process_start_daltonize(message):
    if (message.content_type == 'photo'):
        try:  
           chat_id = message.chat.id
           user_dict[chat_id] = message
           markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
           markup.resize_keyboard = True
           markup.add('Yes', 'No')
           msg = bot.reply_to(message, "Daltonic bot has detected a new image. Do you want to daltonize it?", reply_markup=markup)
           bot.register_next_step_handler(msg, process_option_choose)
        except Exception as e:
           print(e)

def process_option_choose(message):
    try:
        option = message.text
        if (option == u'Yes'):
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.resize_keyboard = True
            markup.add('Deuteranopia', 'Protanopia', 'Tritanopia')
            msg = bot.reply_to(message, "Choose daltonic option", reply_markup=markup)
            bot.register_next_step_handler(msg, process_daltonize_now)
    except Exception as e:
        print(e)

def process_daltonize_now(msg):
    message = user_dict[msg.chat.id]
    cid = message.chat.id
    if (message.content_type == 'photo'):
        try:
           daltonic_option = msg.text.lower()
           file_id = message.photo[1].file_id
           file_path = bot.get_file(file_id).file_path
           if (not(file_path.find("jpg")) or not(file_path.find("png"))):
              send_message(cid, "Please send png or jpg files")
           else:
              send_message(cid, "Processing image...")
              file = download_image(file_id)
              input_image_path = save_file(file)
              random_string = system_call("/usr/bin/head /dev/urandom | tr -dc A-Za-z0-9 | /usr/bin/head -c 5 | xargs echo").lower()
              send_message(cid, "Adjusting image....")
              output_image_path = SAVE_PATH + '/outcoming_images/new_file_' + current_time() + "_" + random_string + '.png'
              touch(output_image_path)
              adjust_image(input_image_path, output_image_path, daltonic_option)
              send_message(cid, "Sending new image....")
              send_photo(cid, output_image_path)
              send_message(cid, "New image sended!")
        except ValueError:
            send_message(cid, "Unexpected error. Please try again.")
    else:
       send_message(cid, "Please send an image to adjust for colour blind people.")
  
#bot.polling(none_stop=True, interval=0)
bot.polling(none_stop=False, interval=0)
