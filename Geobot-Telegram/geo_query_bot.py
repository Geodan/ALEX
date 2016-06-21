
if __name__ == "__main__":
    with open('token.txt') as token_file:
        token = token_file.read()
    bot = telebot.TeleBot(token.strip())
