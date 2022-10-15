import csv
import os
import re
from datetime import datetime, timedelta
import sys

from telethon import TelegramClient, events, sync

from secret import api_id, api_hash  # At first we have to create an APP and get
                                     # api_id and api_hash from telegram to start use
                                     # telegram api


def get_user_dialog_from_args(dialogs):
    if len(sys.argv) > 1:
        dialog_chanels = [dialog for dialog in sys.argv if re.search('channel', dialog) is not None]

        if len(dialog_chanels) == 0:
            try:
                if len(sys.argv) > 2:
                    dialog_name = ' '.join([arg for arg in sys.argv if re.search('telegram_message_getter', arg) is None]).strip()
                    users_dialog = [d for d in dialogs if d.title == dialog_name]
                else:
                    users_dialog = [d for d in dialogs if d.title == sys.argv[1]]

                if len(users_dialog) == 0:
                    print('--incorrect chat name--')

                return users_dialog
            except Exception as err:
                print('dialog exception -->', err)
                return []
        else:
            try:
                if re.search(r'nochannel', dialog_chanels[0]) is not None:
                    users_dialog = [d for d in dialogs if d.is_channel is False]
                else:
                    users_dialog = [d for d in dialogs if d.is_channel is True and d.is_group is False]
                return users_dialog
            except Exception as err:
                print('channel parametr error --->', err)
                return []
    return dialogs


def get_user_params_and_write_data_to_csv(filename, chat_history, file_existed=False,):
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
    try:
        user_id_set = {message['user_id'] for message in chat_history}
    except Exception:
        user_id_set = set()

    # print('user_id_set -->', user_id_set)

    users_list = []
    for user in user_id_set:
        if not user:
            first_name, last_name, phone, username = '', '', '', ''
        else:
            first_name = client.get_entity(user).first_name
            last_name = client.get_entity(user).last_name
            phone = client.get_entity(user).phone
            username = client.get_entity(user).username

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
    folder_to_save_chats = '/home/user/telegram_history/'
    os.chdir(folder_to_save_chats)

    session_name = os.environ.get('TG_SESSION', 'printer')

    client = TelegramClient(session_name, api_id, api_hash)
    client.start()

    dialogs = [d for d in client.iter_dialogs()]

    dialogs = get_user_dialog_from_args(dialogs)

    with client:
        for dialog in dialogs:
            # print(dialog.__dict__)
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
                filename = folder_to_save_chats + dialog.title.replace('/', '') + '.csv'
                print('new  - {} -  file will be created'.format(filename))

                client.loop.run_until_complete(get_all_chat_history())
                chat_history = get_user_info(client, chat_history)
                get_user_params_and_write_data_to_csv(filename, chat_history)

            print(dialog.title + '--> Done')
            print()
    print('Finished')


