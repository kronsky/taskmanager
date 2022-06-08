import time
from bot import bot
from taskmanager import unix_time_now, Table, Task


def notification():
    while True:
        now = unix_time_now()
        for table in Table.get_tables():
            tasks = Task.get_deadlines(int(table[0]))
            for task in tasks:
                time_notification = task[2] - task[1]
                if time_notification <= now < time_notification + 60:
                    bot.send_message(int(table[0]), f'Вы должны выполнить задачу: {task[0]}')
                if task[3] <= now < task[3] + 60:
                    Task.overdue_task(int(table[0]), task[4])
                    bot.send_message(int(table[0]), f'Вы просрочили задачу: {task[0]}')
        time.sleep(60)
