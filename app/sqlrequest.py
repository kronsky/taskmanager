import time
import sqlite3
import logging

logger = logging.getLogger('taskmanager')
handler = logging.FileHandler('logs.txt')
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


class DataConnection:
    def __init__(self):
        self.db_name = 'db/taskmanager.db'

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        if exc_val:
            logger.error('database error: ' + str(exc_val))


def create_table():
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT count(name) FROM sqlite_master 
                        WHERE type='table' AND name='users'
                        """)
        if cursor.fetchone()[0] != 1:
            cursor.execute("""CREATE TABLE users(
                        chatid integer,
                        name text
                    )""")
        connection.commit()


class User(object):
    def __init__(self, chatid, name):
        self.chatid = chatid
        self.name = name

    def add_user(self):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT chatid FROM users WHERE chatid = {self.chatid}")
            chat = cursor.fetchall()
            if not len(chat):
                cursor.execute(f"INSERT INTO users (chatid, name)  VALUES  ({self.chatid},"
                               f" '{self.name}')")
                cursor.execute(f"CREATE TABLE tasks_{self.chatid}(title text, description text,"
                               f" tag text, dt_create int, dt_start int, dt_deadline int,"
                               f" dt_begin int, dt_end int, reminder int, status text, runtime int)")
            connection.commit()
            logger.info('добавлен новый пользовтаель: ' + str(self.chatid))


class Task(object):
    def __init__(self, chat_id, title, description, tag, reminder, dt_create, dt_start,
                 dt_deadline, dt_begin, dt_end, status, runtime):
        self.chat_id = chat_id
        self.title = title
        self.description = description
        self.tag = tag
        self.reminder = reminder
        self.dt_create = dt_create
        self.dt_start = dt_start
        self.dt_deadline = dt_deadline
        self.dt_begin = dt_begin
        self.dt_end = dt_end
        self.status = status
        self.runtime = runtime

    def add_task(self):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"""INSERT INTO tasks_{self.chat_id} 
            (title, description, tag, reminder, dt_create, dt_start, 
            dt_deadline, dt_begin, dt_end, status, runtime)  
            VALUES  ('{self.title}', '{self.description}', '{self.tag}',
            '{self.reminder}', '{self.dt_create}', '{self.dt_start}', 
            '{self.dt_deadline}', '{self.dt_begin}', '{self.dt_end}', 
            '{self.status}', '{self.runtime}')""")
            logger.info(f'Создана новая задача пользователем {self.chat_id}')
            connection.commit()

    @staticmethod
    def get_tasks(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT rowid, * FROM tasks_{str(chatid)} WHERE status <> 'completed'"
                           f" and status <> 'overdue'")
            return cursor.fetchall()

    @staticmethod
    def get_all_tasks(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT rowid, * FROM tasks_{str(chatid)}")
            return cursor.fetchall()

    @staticmethod
    def begin_task(chatid, rowid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            begin = int(time.time())
            cursor.execute(f"UPDATE tasks_{chatid} SET dt_begin = {begin} WHERE rowid = {rowid}")
            cursor.execute(f"UPDATE tasks_{chatid} SET status = 'begined' WHERE rowid = {rowid}")
            connection.commit()

    @staticmethod
    def end_task(chatid, rowid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            end = int(time.time())
            cursor.execute(f"UPDATE tasks_{chatid} SET dt_end = {end} WHERE rowid = {rowid}")
            cursor.execute(f"UPDATE tasks_{chatid} SET status = 'completed' WHERE rowid = {rowid}")
            cursor.execute(f"SELECT dt_begin FROM tasks_{str(chatid)} WHERE rowid = {rowid}")
            dt_begin = cursor.fetchall()
            cursor.execute(f"SELECT dt_end FROM tasks_{str(chatid)} WHERE rowid = {rowid}")
            dt_end = cursor.fetchall()
            runtime = int(dt_end[0][0]) - int(dt_begin[0][0])
            cursor.execute(f"UPDATE tasks_{chatid} SET runtime = {runtime} WHERE rowid = {rowid}")
            connection.commit()

    @staticmethod
    def del_task(chatid, rowid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM tasks_{chatid} WHERE rowid = {rowid}")
            connection.commit()

    @staticmethod
    def get_runtime(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT runtime FROM tasks_{str(chatid)}")
            return cursor.fetchall()

    @staticmethod
    def get_status(chatid, rowid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT status FROM tasks_{str(chatid)} WHERE rowid = {rowid}")
            return cursor.fetchall()[0][0]

    @staticmethod
    def get_deadlines(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT title, reminder, dt_start, dt_deadline, rowid "
                           f"FROM tasks_{str(chatid)} WHERE status = 'created'")
            return cursor.fetchall()

    @staticmethod
    def overdue_task(chatid, rowid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE tasks_{chatid} SET status = 'overdue' WHERE rowid = {rowid}")
            connection.commit()

    @staticmethod
    def get_overdue_task(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT rowid, * FROM tasks_{str(chatid)} WHERE status = 'overdue'")
            return cursor.fetchall()

    @staticmethod
    def get_completed_tasks(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT rowid, * FROM tasks_{str(chatid)} WHERE status = 'completed'")
            return cursor.fetchall()


def get_tables():
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT name from sqlite_master where type= "table"')
        return cursor.fetchall()


create_table()
