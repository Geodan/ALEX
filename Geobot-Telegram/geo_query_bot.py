import requests
import telebot
import json
import urllib

if __name__ == "__main__":
    with open('token.txt') as token_file:
        token = token_file.read()
    bot = telebot.TeleBot(token.strip())

    @bot.message_handler(commands=['query'])
    def query(message):
        print(message.chat)
        bot.send_chat_action(message.chat.id, 'find_location')

        arguments = message.text.split(" ")

        if len(arguments) < 2:
            bot.reply_to(message, "Please supply a query.")
            return

        url = 'http://localhost:8085/parse_and_run_query'
        payload = {'sentence': " ".join(arguments[1:])}
        headers = {'content-type': 'application/json'}

        response = requests.post(url, data=json.dumps(payload), headers=headers)
        bot.reply_to(message, response.content.decode("utf-8"))


    bot.polling(none_stop=True)
