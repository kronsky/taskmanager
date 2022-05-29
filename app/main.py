from multiprocessing.context import Process
from notification import notification
from bot import bot


if __name__ == '__main__':
    Process(target=notification).start()
    bot.polling(none_stop=True)
