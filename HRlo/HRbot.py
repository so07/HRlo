import os
import sys
import re

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import datetime
import configparser
from threading import Thread

from . import HRauth, HRlo, HRget, HRday, HRphone, HRpresence, utils

def get_token(config_file):
    parser = configparser.ConfigParser()
    parser.read(config_file)
    return parser.get('HRbot', 'token')

def get_today():
   date_today = datetime.datetime.today()
   json = hr_get.get(year=date_today.year, month=date_today.month, day=date_today.day)
   hr_today = HRday.HRday(json)
   return hr_today

def get_hrlo():
    return HRlo.HRlo(hr_auth)

config_file = HRauth.HRauth_default['config_file']
token = get_token(config_file)

bot = Bot(token=token)
updater = Updater(token=token)

hr_auth  = HRauth.HRauth()
hr_get   = HRget.HRget(hr_auth)
hr_phone = HRphone.HRphone(hr_get.phone())
hr_today = get_today()

def _message_format(msg):
    return re.sub(r"[.\.]+", "\n", msg)

def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def hrlo(bot, update):
    keyboard = [ 
               [
                 KeyboardButton("/time", True, True),
                 KeyboardButton("/stamp", True, True),
               ],
               [
                 KeyboardButton("/exit", True, True),
               ],
               ]
    #reply_markup = telegram.ReplyKeyboardMarkup(keyboard)

    keyboard = [
               [
                 InlineKeyboardButton("time", callback_data='time'),
                 InlineKeyboardButton("stamp", callback_data='stamp'),
               ],
               [
                 InlineKeyboardButton("exit", callback_data='exit'),
               ],
               #[
               #  InlineKeyboardButton("in", callback_data='presence'),
               #  InlineKeyboardButton("phone", callback_data='phone'),
               #  InlineKeyboardButton("name", callback_data='name'),
               #],
               #[
               #  InlineKeyboardButton("day", callback_data='day'),
               #  InlineKeyboardButton("week", callback_data='week'),
               #  InlineKeyboardButton("month", callback_data='month'),
               #]
               ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('HRlo inline button commands:', reply_markup=reply_markup)
    update.message.reply_text('type /help for more commands')

def bot_print(bot, update, msg):
    #msg = re.sub(r"[.\.]+", "\n", msg)
    bot.sendMessage(parse_mode='HTML', chat_id=update.message.chat.id, text='<pre>'+msg+'</pre>')
    #bot.send_message(chat_id=update.message.chat_id, text="`" + msg + "`", parse_mode=telegram.ParseMode.MARKDOWN)

def call_hrlo(func):
    def wrapped(bot, update, *args, **kwargs):
        ret = func(bot, update, *args, **kwargs)
        hrlo(bot, update)
        return ret
    return wrapped

def login(bot, update):
    if hr_auth.login():
        msg = "successfully login"
    else:
        msg = "invalid login!!!"
    msg += "\nuser {}".format(hr_auth.username())
    msg += "\nhost {}".format(hr_auth.host())
    msg += "\nid   {}".format(hr_auth.idemploy())
    bot_print(bot, update, msg)

@call_hrlo
def day(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    hr = get_hrlo()
    msg = hr.report_day()
    msg = _message_format(msg)
    bot_print(bot, update, msg)

@call_hrlo
def week(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    hr = get_hrlo()
    msg = hr.report_week()
    msg = _message_format(msg)
    bot_print(bot, update, msg)

@call_hrlo
def week_month(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    hr = get_hrlo()
    msg = hr.report_month_weeks()
    msg = _message_format(msg)
    bot_print(bot, update, msg)

@call_hrlo
def month(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    hr = get_hrlo()
    msg = hr.report_month()
    msg = _message_format(msg)
    bot_print(bot, update, msg)

@call_hrlo
def exit(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    hr_today = get_today()
    msg = "Today {} Exits:\n".format(hr_today.date().date())
    lunch = True
    least = False
    msg += "Standard time   [{}]\n  Exit   @ {}\n  Remains  {}\n".format(
            hr_today.HR_workday,
            str(hr_today.exit(lunch=lunch, least=least).strftime("%H:%M")),
            utils.to_str(hr_today.remains(lunch=lunch, least=least)),
            )
    lunch = True
    least = True
    msg += "At Least lunch  [{}]\n  Exit   @ {}\n  Remains  {}\n".format(
            hr_today.HR_workday_least_with_lunch,
            str(hr_today.exit(lunch=lunch, least=least).strftime("%H:%M")),
            utils.to_str(hr_today.remains(lunch=lunch, least=least)),
            )
    lunch = False
    least = True
    msg += "At Least work   [{}]\n  Exit   @ {}\n  Remains  {}\n".format(
            hr_today.HR_workday_least,
            str(hr_today.exit(lunch=lunch, least=least).strftime("%H:%M")),
            utils.to_str(hr_today.remains(lunch=lunch, least=least)),
            )
    bot_print(bot, update, msg)

@call_hrlo
def stamp(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    hr_today = get_today()
    msg = "Today {} Stamps:\n".format(hr_today.date().date())
    msg += "[{}]\n".format( ", ".join([ i.time().strftime("%H:%M") for i in hr_today.logs()]))
    bot_print(bot, update, msg)

@call_hrlo
def time(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    hr_today = get_today()
    msg = "Today {} Times:\n".format(hr_today.date().date())
    msg += "Uptime         {}\n".format(hr_today.uptime())
    msg += "Worked time %  {:.1f}\n".format( 100.0*hr_today.uptime().total_seconds()/hr_today.time_to_work())
    msg += "Time to work   {}\n".format(utils.to_str(hr_today.time_to_work()))
    msg += "Timenet        {}\n".format(utils.to_str(hr_today.timenet()))
    msg += "Lunch time     {}\n".format(utils.to_str(hr_today['time_lunch']))
    msg += "KO time        {}\n".format(utils.to_str(hr_today['time_ko']))
    bot_print(bot, update, msg)
    return msg

@call_hrlo
def presence(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    hr_presence = HRpresence.HRpresence(hr_get.presence())
    msg = "Workers status:\n"
    msg += hr_presence.report(args)
    bot_print(bot, update, msg)

@call_hrlo
def phone(bot, update, args):
    msg = "Workers phone numbers:\n"
    msg += hr_phone.report(args, [])
    bot_print(bot, update, msg)

@call_hrlo
def name(bot, update, args):
    msg = "Workers phone numbers:\n"
    msg += hr_phone.report([], args)
    bot_print(bot, update, msg)

@call_hrlo
def help(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    msg = """HRbot help

/hrlo
   inline button command

/exit
   estimated exit times
/stamp
   time stamps
/time
   today times report

/in name [name ...]
   get worker status
/phone name [name ...]
   get phone number from worker name
/name 12345 [12345 ...]
   get worker name from phone number

/restart
   restart HRbot

/help
   print this help
    """
    update.message.reply_text(msg)
    #bot_print(bot, update, msg)

def button(bot, update):
    query = update.callback_query
    globals()[query.data](bot, query)

def stop(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text="stop me please")
    updater.stop()

def stop_and_restart():
    updater.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)

def restart(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    update.message.reply_text('HRbot is restarting ...')
    Thread(target=stop_and_restart).start()

def main():

    # echo handler
    updater.dispatcher.add_handler( MessageHandler(Filters.text, hrlo) )

    updater.dispatcher.add_handler( CommandHandler('hrlo', hrlo) )

    updater.dispatcher.add_handler( CommandHandler('day', day) )
    updater.dispatcher.add_handler( CommandHandler('week', week) )
    updater.dispatcher.add_handler( CommandHandler('week_month', week_month) )
    updater.dispatcher.add_handler( CommandHandler('month', month) )

    updater.dispatcher.add_handler( CommandHandler('exit', exit) )
    updater.dispatcher.add_handler( CommandHandler('stamp', stamp) )
    updater.dispatcher.add_handler( CommandHandler('time', time) )

    updater.dispatcher.add_handler( CommandHandler('help', help) )

    updater.dispatcher.add_handler( CommandHandler('in', presence, pass_args=True) )
    updater.dispatcher.add_handler( CommandHandler('phone', phone, pass_args=True) )
    updater.dispatcher.add_handler( CommandHandler('name', name, pass_args=True) )

    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.dispatcher.add_handler( CommandHandler('login', login) )

    # stop and restart HRbot
    updater.dispatcher.add_handler( CommandHandler('stop', stop ))
    updater.dispatcher.add_handler( CommandHandler('restart', restart))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
   main()

