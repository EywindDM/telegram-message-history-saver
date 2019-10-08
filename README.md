# telegram-message-history-saver
Use this simple script to save all messages in Telegram from any chat (in .csv)

1. copy all files *.py to any empty folder on your machine
2. go to https://core.telegram.org/api and create an applicattion.
3. copy api_id and api_hash to secret.py
4. open terminal and install all dependences from requirements.txt (pip3 install -r requirements.txt)
5. How to use it:
   python3 telegram_message_getter.py (copy all chats to folder where locate script, it can require hours...)
   python3 telegram_message_getter.py MyFriend (copy all messages from chat with name MyFriend. If chat name consist spaces like 'My Friend' ignore it and write 'MyFriend', should work)   
   python3 telegram_message_getter.py MyFriend 100 (copy last 100 messages from chat with name MyFriend)




