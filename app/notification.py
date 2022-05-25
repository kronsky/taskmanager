import time
from bot import bot
from sqlrequest import get_tables, Task


def notification():
    while True:
        now = int(time.time())
        # цикл по всем таблицам
        for table in get_tables():
            # если имя таблицы table*, то цикл по актуальным задачам
            if table[0][:5] == 'tasks':
                userid = table[0][6:]
                tasks = Task.get_deadlines(userid)
                for task in tasks:
                    time_notification = task[2] - task[1]
                    # отправка уведомления, если текущее время равно или больше,
                    # но меньше времени увидомления на 60 сеукнд (запрос раз в 60 секунд)
                    if (time_notification <= now) and (time_notification + 60 > now):
                        bot.send_message(userid, f'Вы должны выполнить задачу: {task[0]}')
                    # если текущее время больше крайнего срока, то присвение статуса overdue
                    if (task[3] <= now) and (task[3] + 60 > now):
                        Task.overdue_task(userid, task[4])
                        bot.send_message(userid, f'Вы просрочили задачу: {task[0]}')
        time.sleep(60)
