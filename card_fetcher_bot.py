#!/usr/bin/env python3

from http.client import TEMPORARY_REDIRECT
import logging
import requests
import configparser
from telegram import MessageEntity, Update
from telegram.ext import Updater, CallbackContext
from telegram.ext import MessageHandler, Filters


config = configparser.ConfigParser()
config.read("config.ini")

telegram_token = config["telegram"]["token"]
logfile = config["logging"]["logfile"]
api_url = config["api"]["url"]

# define logging
logging.basicConfig(
    filename=logfile,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def get_magic_card(cardname):
    logging.debug(f"Cardname to search for: {cardname}")
    if cardname and len(cardname) > 0:
        payload = {"fuzzy": cardname}
        logging.debug(f"API payload: {payload}")
        try:
            r = requests.get(api_url, params=payload)
            logging.debug(f"Response: {r.text}")
        except:
            raise

        if r.status_code == 200:
            card = r.json()
            answer = card["image_uris"]["normal"]
        elif r.status_code == 404:
            if "type" in r.json() and r.json()["type"] == "ambiguous":
                answer = "Found more than 1 card, please be more specific"
            else:
                answer = f"No matching card for '{cardname}' found. Try again"
        else:
            logging.error(r.text)
            answer = "whoopsie"
    else:
        answer = "Got an empty message"

    return answer


# try to find magic cards when mentioned in groups
def fetch_from_group(update: Update, context: CallbackContext):
    logging.debug(f"Bot name: {context.bot.name}")
    logging.debug(f"Message text: {update.message.text}")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_magic_card(update.message.text.replace(context.bot.name, "")),
    )


# try to find magic cards when messaged directly
def fetch_from_dm(update: Update, context: CallbackContext):
    logging.debug(f"Bot name: {context.bot.name}")
    logging.debug(f"Direct Message text: {update.message.text}")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_magic_card(update.message.text),
    )


def main():
    updater = Updater(token=telegram_token)
    dispatcher = updater.dispatcher

    # define and add handler for groups
    group_handler = MessageHandler(
        Filters.text
        & Filters.entity(MessageEntity.MENTION)
        & Filters.regex(updater.bot.name),
        fetch_from_group,
    )
    dispatcher.add_handler(group_handler)

    # define and add handler for direct messages
    direct_message_handler = MessageHandler(Filters.chat_type.private, fetch_from_dm)
    dispatcher.add_handler(direct_message_handler)

    # fire it up
    updater.start_polling()


if __name__ == "__main__":
    main()
