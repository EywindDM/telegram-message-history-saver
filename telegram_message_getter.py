import csv
import os
import time
from datetime import datetime
import sys

from telethon import TelegramClient, events, sync

from secret import api_id, api_hash  # At first we have to create an APP and get
                                     # api_id and api_hash from telegram to start use
                                     # telegram api


def get_env(name, message, cast=str):
    if name in os.environ:
        return os.environ[name]
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e, file=sys.stderr)
            time.sleep(1)


def get_user_dialog_from_args(dialogs):
    for d in dialogs:
        if d.title.replace(' ', '') == sys.argv[1]:
            users_dialog = d
            break
    try:
        users_dialog
    except Exception:
        print()
        print("ERROR --> user's dialog not found")
        print()

    return [users_dialog]


def get_user_params_and_write_data_to_csv(dialog, chat_history, not_full_chat=False):
    if not_full_chat:
        filename = dialog.title.replace('/', '') + '_' + sys.argv[-1] + '_messages_' + str(datetime.now()).split('.')[0].replace(' ', '_')+ '.csv'
    else:
        filename = dialog.title.replace('/', '') + '.csv'

    with open(filename, 'a', encoding='utf-8-sig', newline='') as f:
        file = csv.writer(f, dialect='excel')
        file.writerow(['user_id', 'first_name', 'last_name', 'username', 'phone', 'message_id', 'date', 'text'])

        for message in chat_history:
            try:
                first_name = client.get_entity(message['user_id']).first_name
            except Exception:
                first_name = ''

            try:
                last_name = client.get_entity(message['user_id']).last_name
            except Exception:
                last_name = ''

            try:
                username = client.get_entity(message['user_id']).username
            except Exception:
                username = ''

            try:
                phone = client.get_entity(message['user_id']).phone
            except Exception:
                phone = ''

            file.writerow([message['user_id'],
                           first_name,
                           last_name,
                           username,
                           phone,
                           message['message_id'],
                           message['date'],
                           message['text']])
        f.close()


async def get_all_chat_history():
    async for message in client.iter_messages(chat_entity, reverse=True):
        if message.message != '' and message.message != None:
            chat_history.append({'message_id': message.id,
                                 'user_id': message.from_id,
                                 'date': str(message.date).split('+')[0],
                                 'text': message.message})


async def get_last_chat_history(messages_quantity):
    async for message in client.iter_messages(chat_entity, reverse=False, limit=int(messages_quantity)):
        if message.message != '' and message.message != None:
            chat_history.append({'message_id': message.id,
                                 'user_id': message.from_id,
                                 'date': str(message.date).split('+')[0],
                                 'text': message.message})


if __name__ == '__main__':
    session_name = os.environ.get('TG_SESSION', 'printer')

    client = TelegramClient(session_name, api_id, api_hash)
    client.start()

    dialogs = [d for d in client.iter_dialogs()]

    if len(sys.argv) == 3:
        dialogs = get_user_dialog_from_args(dialogs)

        with client:
            for dialog in dialogs:
                print('start -->', dialog.title, sys.argv[-1])
                chat_entity = client.get_entity(dialog)
                chat_history = []
                client.loop.run_until_complete(get_last_chat_history(sys.argv[-1]))

                chat_history.reverse()
                get_user_params_and_write_data_to_csv(dialog, chat_history, not_full_chat=True)
                print(dialog.title + ' ' + sys.argv[-1] + '--> Done')
    else:
        if len(sys.argv) == 2:
            dialogs = get_user_dialog_from_args(dialogs)

        with client:
            for dialog in dialogs:
                print('start -->', dialog.title)
                chat_entity = client.get_entity(dialog)
                chat_history = []
                client.loop.run_until_complete(get_all_chat_history())

                get_user_params_and_write_data_to_csv(dialog, chat_history)
                print(dialog.title + '--> Done')
    print('Finished')

