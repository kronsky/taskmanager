import time
import unittest
from taskmanager import Table, Task


class TestTask(unittest.TestCase):

    def setUp(self):
        self.task = Task('1234', 'test', 'test task', 10, 1654516286, 1654516286)
        Table.create_table(1234)
        self.task.write(1234)

    def test_add(self):
        self.assertEqual(self.task.chatid, 1234)
        self.assertEqual(self.task.title, 'test')
        self.assertEqual(self.task.description, 'test task')
        self.assertEqual(self.task.reminder, 10)
        self.assertEqual(self.task.start, 1654516286)
        self.assertEqual(self.task.deadline, 1654516286)
        self.assertEqual(self.task.status, 'created')
        self.assertIn(('1234',), Table.get_tables())
        self.assertEqual(Task.get_tasks(1234)[0][0], 1)
        self.assertEqual(Task.get_tasks(1234)[0][5], 1654516286)
        self.assertEqual(Task.get_tasks(1234)[0][10], 'created')

    def test_delete(self):
        Task.delete(1234, 1)
        self.assertTrue(len(Task.get_tasks(1234)) == 0)

    def test_begin(self):
        Task.begin(1234, 1)
        self.assertEqual(Task.get_status(1234, 1), 'begined')
        self.assertTrue(type(Task.get_tasks(1234)[0][7]) != 'None')

    def test_end(self):
        Task.begin(1234, 1)
        Task.end(1234, 1)
        self.assertEqual(Task.get_status(1234, 1), 'completed')
        self.assertTrue(type(Task.get_all_tasks(1234)[0][8]) != 'None')
        self.assertTrue(type(Task.get_all_tasks(1234)[0][9]) != 'None')

    def test_overdue(self):
        Task.overdue_task(1234, 1)
        self.assertEqual(Task.get_status(1234, 1), 'overdue')

    def test_runtime(self):
        Task.begin(1234, 1)
        time.sleep(2)
        Task.end(1234, 1)
        self.assertEqual(Task.get_runtime(1234)[0][0], 2)

    def tearDown(self):
        Table._drop_table('1234')


if __name__ == '__main__':
    unittest.main()
