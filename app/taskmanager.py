from datetime import datetime
import sqlite3
import pytz
import logging
from config import time_zone

logger = logging.getLogger(__name__)
handler = logging.FileHandler('logs.txt')
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def unix_time_now():
    return int(datetime.now(tz=pytz.timezone(time_zone)).strftime("%s"))


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


class Task:
    def __init__(self, chatid, title, description, reminder, start, deadline):
        self.chatid = chatid
        self.title = title
        self.description = description
        self.creation = unix_time_now()
        self.reminder = reminder
        self.start = start
        self.deadline = deadline
        self.begin = None
        self.end = None
        self.runtime = None
        self.status = 'created'

    def __str__(self):
        return f'chatid = {self.chatid} title = {self.title}, ' \
               f'description = {self.description}, date of creation = {self.creation}'

    @property
    def chatid(self):
        return self.__chatid

    @chatid.setter
    def chatid(self, chatid):
        try:
            self.__chatid = int(chatid)
        except ValueError:
            logger.critical('a non-numeric field chatid is entered')

    @property
    def reminder(self):
        return self.__reminder

    @reminder.setter
    def reminder(self, reminder):
        try:
            self.__reminder = int(reminder)
        except ValueError:
            logger.critical('a non-numeric field reminder is entered')

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, start):
        try:
            self.__start = int(start)
        except ValueError:
            logger.critical('a non-numeric field start is entered')

    @property
    def deadline(self):
        return self.__deadline

    @deadline.setter
    def deadline(self, deadline):
        try:
            self.__deadline = int(deadline)
        except ValueError:
            logger.critical('a non-numeric field deadline is entered')

    @staticmethod
    def create_table(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"""SELECT count(name) FROM sqlite_master 
                                    WHERE type='table' AND name='{chatid}'""")
            if cursor.fetchone()[0] != 1:
                cursor.execute(f"""CREATE TABLE '{chatid}'(title text, description text,
                               creation int, reminder int, start int, deadline int,
                               begin int, end int, runtime int, status text)""")
                connection.commit()
                logger.info('added a new user table: ' + str(chatid))

    def write(self, chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"""INSERT INTO '{chatid}'
                        (title, description, creation, reminder, start, 
                        deadline, begin, end, runtime, status)  
                        VALUES  ('{self.title}', '{self.description}',
                        '{self.creation}', '{self.reminder}', '{self.start}', 
                        '{self.deadline}', '{self.begin}', '{self.end}', 
                        '{self.runtime}', '{self.status}')""")
            logger.info(f'A new task has been created by the user: {chatid}')
            connection.commit()

    @staticmethod
    def table_is(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{chatid}'")
            if cursor.fetchall():
                return True
            else:
                return False

    @staticmethod
    def get_tasks(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT rowid, * FROM '{chatid}' WHERE status <> 'completed'"
                           f" and status <> 'overdue'")
            return cursor.fetchall()

    @staticmethod
    def get_all_tasks(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT rowid, * FROM '{chatid}'")
            return cursor.fetchall()

    @staticmethod
    def get_status(chatid, rowid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT status FROM '{chatid}' WHERE rowid = {rowid}")
            return cursor.fetchall()[0][0]

    @staticmethod
    def get_overdue_task(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT rowid, * FROM '{chatid}' WHERE status = 'overdue'")
            return cursor.fetchall()

    @staticmethod
    def get_completed_tasks(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT rowid, * FROM '{chatid}' WHERE status = 'completed'")
            return cursor.fetchall()

    @staticmethod
    def get_deadlines(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT title, reminder, start, deadline, rowid "
                           f"FROM '{chatid}' WHERE status = 'created'")
            return cursor.fetchall()

    @staticmethod
    def get_runtime(chatid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT runtime FROM '{chatid}'")
            return cursor.fetchall()

    @staticmethod
    def begin(chatid, rowid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE '{chatid}' SET begin = {unix_time_now()} WHERE rowid = {rowid}")
            cursor.execute(f"UPDATE '{chatid}' SET status = 'begined' WHERE rowid = {rowid}")
            connection.commit()
        logger.info(f'the user {chatid} has started to perform the task {rowid}')

    @staticmethod
    def end(chatid, rowid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            timenow = unix_time_now()
            cursor.execute(f"UPDATE '{chatid}' SET end = {timenow} WHERE rowid = {rowid}")
            cursor.execute(f"UPDATE '{chatid}' SET begin = {timenow} WHERE rowid = {rowid}"
                           f" AND begin = 'None'")
            cursor.execute(f"UPDATE '{chatid}' SET status = 'completed' WHERE rowid = {rowid}")
            cursor.execute(f"SELECT begin, end FROM '{chatid}' WHERE rowid = {rowid}")
            runtime = cursor.fetchall()
            runtime = runtime[0][1] - runtime[0][0]
            if runtime > 0:
                cursor.execute(f"UPDATE '{chatid}' SET runtime = {runtime} WHERE rowid = {rowid}")
            connection.commit()
        logger.info(f'the user {chatid} has completed the task {rowid}')

    @staticmethod
    def delete(chatid, rowid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM '{chatid}' WHERE rowid = {rowid}")
            connection.commit()
        logger.info(f'the user {chatid} deleted the task {rowid}')

    @staticmethod
    def overdue_task(chatid, rowid):
        with DataConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE '{chatid}' SET status = 'overdue' WHERE rowid = {rowid}")
            connection.commit()
        logger.info(f'the user {chatid} has expired the task {rowid}')


def get_tables():
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name from sqlite_master WHERE type='table'")
        return cursor.fetchall()


def _drop_table(chatid):
    with DataConnection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS '{chatid}'")
