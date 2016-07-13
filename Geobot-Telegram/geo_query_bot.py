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
        payload = {
            'sentence': " ".join(arguments[1:]),
            'location': [52.3426354, 4.9127781]
        }
        headers = {'content-type': 'application/json'}

        response = json.loads(requests.post(url, data=json.dumps(payload), headers=headers).content.decode("utf-8"))
        with open('result.geojson', 'w') as f:
            f.write(str(response["result"]))
        del response["result"]
        bot.reply_to(message, json.dumps(response))
        with open('result.geojson', 'rb') as f:
            bot.send_document(message.chat.id, f)


    bot.polling(none_stop=True)
