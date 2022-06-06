import sqlite3
import logging

logger = logging.getLogger('database')
handler = logging.FileHandler('logs.txt')
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


class DataConnection:
    def __init__(self):
        self.db_name = 'database/taskmanager.db'

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        if exc_val:
            logger.error('database error: ' + str(exc_val))


def create_user_tasks_table(chatid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"""SELECT count(name) FROM sqlite_master 
                                WHERE type='table' AND name='{chatid}'""")
        if cursor.fetchone()[0] != 1:
            cursor.execute(f"""CREATE TABLE '{chatid}'(title text, description text,
                           creation int, reminder int, start int, deadline int,
                           begin int, end int, runtime int, status text)""")
            connection.commit()
            logger.info('add new user table: ' + str(chatid))


def write_task(task, chatid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"""INSERT INTO '{chatid}'
                    (title, description, creation, reminder, start, 
                    deadline, begin, end, runtime, status)  
                    VALUES  ('{task.title}', '{task.description}',
                    '{task.reminder}', '{task.creation}', '{task.start}', 
                    '{task.deadline}', '{task.begin}', '{task.end}', 
                    '{task.runtime}', '{task.status}')""")
        logger.info(f'Создана новая задача пользователем {chatid}')
        connection.commit()


def get_tables_with_chatid(chatid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{chatid}'")
        return cursor.fetchall()


def get_tasks(chatid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT rowid, * FROM '{chatid}' WHERE status <> 'completed'"
                       f" and status <> 'overdue'")
        return cursor.fetchall()


def get_status(chatid, rowid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT status FROM '{chatid}' WHERE rowid = {rowid}")
        return cursor.fetchall()[0][0]


def end_task(chatid, rowid, end_time):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"UPDATE '{chatid}' SET end = {end_time} WHERE rowid = {rowid}")
        cursor.execute(f"UPDATE {chatid}' SET begin = {end_time} WHERE rowid = {rowid}"
                       f" AND dt_begin = 'None'")
        cursor.execute(f"UPDATE {chatid}' SET status = 'completed' WHERE rowid = {rowid}")
        cursor.execute(f"SELECT dt_begin, dt_end FROM tasks_{str(chatid)} WHERE rowid = {rowid}")
        runtime = cursor.fetchall()
        runtime = runtime[0][1] - runtime[0][0]
        if runtime > 0:
            cursor.execute(f"UPDATE tasks_{chatid} SET runtime = {runtime} WHERE rowid = {rowid}")
        connection.commit()
