from multiprocessing.context import Process
from notification import notification
from bot import bot


# запуск процесса уведомлений и запуск опроса сервера ботом
if __name__ == '__main__':
    Process(target=notification).start()
    bot.polling(none_stop=True)
