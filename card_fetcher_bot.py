#!/usr/bin/env python3

from http.client import TEMPORARY_REDIRECT
import logging
import requests
import configparser
from telegram import MessageEntity, Update
from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram.ext import MessageHandler, Filters

# define logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


config = configparser.ConfigParser()
config.read("config.ini")

telegram_token = config["telegram"]["token"]


def get_magic_card(card_name):
    API_URL = "https://api.scryfall.com/cards/named"

    payload = {"fuzzy": card_name}
    if card_name:
        try:
            r = requests.get(API_URL, params=payload)
        except:
            raise

    if r.status_code == 200:
        card = r.json()
        answer = card["image_uris"]["normal"]
    elif r.status_code == 404:
        if "type" in r.json() and r.json()["type"] == "ambiguous":
            answer = "Found more than 1 card, please be more specific"
        else:
            answer = "No card found. Try again"
    else:
        # something strange happened
        answer = "whoopsie"
    return answer


# try to find magic cards when mentioned
def fetch_card(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_magic_card(update.message.text.strip(context.bot.name)),
    )


def main():
    updater = Updater(token=telegram_token)
    dispatcher = updater.dispatcher

    card_handler = MessageHandler(
        Filters.text & Filters.entity(MessageEntity.MENTION), fetch_card
    )
    dispatcher.add_handler(card_handler)

    # fire it up
    updater.start_polling()


if __name__ == "__main__":
    main()
