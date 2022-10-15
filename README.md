# telegram-message-history-saver
Use this simple script to save all messages in Telegram from any chat (in .csv)

1. copy all files *.py to any folder on your machine
2. edit telegram_message_getter.py --> folder_to_save_chats = '' . give it a path to folder where you want to write telegram chats .csv files
3. go to https://core.telegram.org/api and create an applicattion.
4. copy api_id and api_hash to secret.py
5. open terminal, create virual env (python3.7) and install Telethon==1.10.4 or run poetry shell
6. How to use it:
   python3 telegram_message_getter.py (copy all chats)
   python3 telegram_message_getter.py ChatName (copy all messages from chat with name ChatName)
   python3 telegram_message_getter.py channel (copy all messages from chanels (only chanels messages))
   python3 telegram_message_getter.py nochannel (copy messages from all chats except chanels)


