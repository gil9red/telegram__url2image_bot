#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


def get_logger():
    import logging
    import sys

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s')

    fh = logging.FileHandler('log', encoding='utf-8')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)

    return log


log = get_logger()


import config
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from url2image import url2image

from urllib.parse import urlparse


# TODO: проверять валидность url
def ok(url):
    """Функция проверяет, что схема url http или https, и что хостом не является localhost."""

    parse_result = urlparse(url)
    ok_scheme = parse_result.scheme == 'http' or parse_result.scheme == 'https'

    return parse_result.netloc != 'localhost' and ok_scheme


class BadUrlError(Exception):
    pass


# Отправка сообщения на команду /start
def start(bot, update):
    log.debug('help')

    bot.sendMessage(chat_id=update.message.chat_id, disable_web_page_preview=True, text=config.START_TEXT)


# Отправка сообщения на команду /help
def help(bot, update):
    log.debug('start')

    bot.sendMessage(update.message.chat_id, text=config.HELP_TEXT)


def work(bot, update):
    log.debug('work')

    try:
        url = update.message.text
        log.debug('Url: %s', url)

        url = url.strip()
        if not ok(url):
            raise BadUrlError()

        url2image(url, config.FILE_NAME)

        # TODO: слишком большие фотки телеграмм уменьшает в разы и тогда картнки становятся нечитаемые
        with open(config.FILE_NAME, 'rb') as f:
            bot.sendPhoto(update.message.chat_id, f)

    except BadUrlError as e:
        log.warning('Bad url: %s', e)
        bot.sendMessage(update.message.chat_id, config.BAD_URL_ERROR_TEXT)

    except Exception as e:
        log.exception(e)
        bot.sendMessage(update.message.chat_id, config.ERROR_TEXT)


def error(bot, update, error):
    log.warn('Update "%s" caused error "%s"' % (update, error))


if __name__ == '__main__':
    log.debug('Start')

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(config.TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler([Filters.text], work))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    log.debug('Finish')
