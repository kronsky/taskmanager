from threading import Thread
from notification import notification
from bot import bot


if __name__ == '__main__':
    Thread(target=notification).start()
    bot.polling(none_stop=True)
