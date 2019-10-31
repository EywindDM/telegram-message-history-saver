import csv
import os
import time
from datetime import datetime, timedelta
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
    try:
        for d in dialogs:
            if d.title.replace(' ', '') == sys.argv[1]:
                users_dialog = d
                break
        return [users_dialog]
    except Exception:
        return dialogs


def get_user_params_and_write_data_to_csv(filename,
                                          chat_history,
                                          file_existed=False,):

    with open(filename, 'a+', encoding='utf-8-sig', newline='') as f:
        file = csv.writer(f, dialect='excel')

        if not file_existed:
            file.writerow(['user_id', 'first_name', 'last_name', 'username', 'phone', 'message_id', 'date', 'text'])

        for message in chat_history:
            file.writerow([message['user_id'],
                           message['first_name'],
                           message['last_name'],
                           message['username'],
                           message['phone'],
                           message['message_id'],
                           message['date'],
                           message['text']])
        print('{} - messages saved'.format(len(chat_history)))
        f.close()


async def get_all_chat_history():
    async for message in client.iter_messages(chat_entity, reverse=True):
        if message.message != '' and message.message != None:
            chat_history.append({'message_id': message.id,
                                 'user_id': message.from_id,
                                 'date': str(message.date).split('+')[0],
                                 'text': message.message})


async def get_last_chat_history_by_date(last_message_date):
    async for message in client.iter_messages(chat_entity, reverse=True, offset_date=last_message_date):
        if message.message != '' and message.message != None:
            chat_history.append({'message_id': message.id,
                                 'user_id': message.from_id,
                                 'date': str(message.date).split('+')[0],
                                 'text': message.message})


def get_user_info(client, chat_history):
    user_id_set = {message['user_id'] for message in chat_history}

    users_list = []
    for user in user_id_set:
        first_name = client.get_entity(user).first_name
        last_name = client.get_entity(user).last_name
        username = client.get_entity(user).username
        phone = client.get_entity(user).phone

        users_list.append({'user_id': user,
                           'first_name': first_name,
                           'last_name': last_name,
                           'username': username,
                           'phone': phone})

    new_chat_history = []
    for message in chat_history:
        for user in users_list:
            if message['user_id'] == user['user_id']:
                new_chat_history.append({'message_id': message['message_id'],
                                         'user_id': message['user_id'],
                                         'first_name': user['first_name'],
                                         'last_name': user['last_name'],
                                         'username': user['username'],
                                         'phone': user['phone'],
                                         'date': message['date'],
                                         'text': message['text']})
                break
    return new_chat_history


if __name__ == '__main__':
    session_name = os.environ.get('TG_SESSION', 'printer')

    client = TelegramClient(session_name, api_id, api_hash)
    client.start()

    dialogs = [d for d in client.iter_dialogs()]
    message_counter = 0

    dialogs = get_user_dialog_from_args(dialogs)

    with client:
        for dialog in dialogs:
            file_existed = False
            try:
                for file_name in os.listdir(os.curdir):
                    if file_name == dialog.title.replace('/', '') + '.csv':
                        with open(file_name) as f:
                            for row in csv.reader(f):
                                if row[6] != '' and row[6] != 'date':
                                    last_message_date = row[6]
                        f.close()
                        file_existed = True
                        filename = file_name
                        break
            except Exception as err:
                print(err)

            chat_entity = client.get_entity(dialog)
            chat_history = []
            if file_existed:
                print('information will be adding to existed file - {}'.format(filename))
                try:
                    last_message_date = datetime.strptime(last_message_date, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=1)
                    client.loop.run_until_complete(get_last_chat_history_by_date(last_message_date))
                    chat_history = get_user_info(client, chat_history)
                    get_user_params_and_write_data_to_csv(filename, chat_history, file_existed=True)
                except Exception:
                    print('0 - messages saved')
            else:
                filename = dialog.title.replace('/', '') + '.csv'
                print('new  - {} -  file will be created'.format(filename))

                client.loop.run_until_complete(get_all_chat_history())
                chat_history = get_user_info(client, chat_history)
                get_user_params_and_write_data_to_csv(filename, chat_history)

            print(dialog.title + '--> Done')
            print()
    print('Finished')

