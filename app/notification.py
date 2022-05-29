import time
from bot import bot
from sqlrequest import get_tables, Task


def notification():
    while True:
        now = int(time.time())
        for table in get_tables():
            if table[0][:5] == 'tasks':
                userid = table[0][6:]
                tasks = Task.get_deadlines(userid)
                for task in tasks:
                    time_notification = task[2] - task[1]
                    # if (time_notification <= now) and (time_notification + 60 > now):
                    if time_notification <= now < time_notification + 60:
                        bot.send_message(userid, f'Вы должны выполнить задачу: {task[0]}')
                    # if (task[3] <= now) and (task[3] + 60 > now):
                    if task[3] <= now < task[3] + 60:
                        Task.overdue_task(userid, task[4])
                        bot.send_message(userid, f'Вы просрочили задачу: {task[0]}')
        time.sleep(60)
