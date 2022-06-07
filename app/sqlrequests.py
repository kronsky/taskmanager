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
                    '{task.creation}', '{task.reminder}', '{task.start}', 
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


def get_all_tasks(chatid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT rowid, * FROM '{chatid}'")
        return cursor.fetchall()


def get_status(chatid, rowid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT status FROM '{chatid}' WHERE rowid = {rowid}")
        return cursor.fetchall()[0][0]


def begin_task(chatid, rowid, begin_time):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"UPDATE '{chatid}' SET begin = {begin_time} WHERE rowid = {rowid}")
        cursor.execute(f"UPDATE '{chatid}' SET status = 'begined' WHERE rowid = {rowid}")
        connection.commit()


def end_task(chatid, rowid, end_time):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"UPDATE '{chatid}' SET end = {end_time} WHERE rowid = {rowid}")
        cursor.execute(f"UPDATE '{chatid}' SET begin = {end_time} WHERE rowid = {rowid}"
                       f" AND begin = 'None'")
        cursor.execute(f"UPDATE '{chatid}' SET status = 'completed' WHERE rowid = {rowid}")
        cursor.execute(f"SELECT begin, end FROM '{chatid}' WHERE rowid = {rowid}")
        runtime = cursor.fetchall()
        runtime = runtime[0][1] - runtime[0][0]
        if runtime > 0:
            cursor.execute(f"UPDATE '{chatid}' SET runtime = {runtime} WHERE rowid = {rowid}")
        connection.commit()


def overdue_task(chatid, rowid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"UPDATE '{chatid}' SET status = 'overdue' WHERE rowid = {rowid}")
        connection.commit()


def del_task(chatid, rowid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM '{chatid}' WHERE rowid = {rowid}")
        connection.commit()


def get_runtime(chatid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT runtime FROM '{chatid}'")
        return cursor.fetchall()


def get_deadlines(chatid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT title, reminder, start, deadline, rowid "
                       f"FROM '{chatid}' WHERE status = 'created'")
        return cursor.fetchall()


def get_overdue_task(chatid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT rowid, * FROM '{chatid}' WHERE status = 'overdue'")
        return cursor.fetchall()


def get_completed_tasks(chatid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT rowid, * FROM '{chatid}' WHERE status = 'completed'")
        return cursor.fetchall()


def get_tables():
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT name from sqlite_master WHERE type="table"')
        return cursor.fetchall()
