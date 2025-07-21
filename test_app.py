import tempfile
import unittest
from os import path

from app import create_app


class TestApplication(unittest.TestCase):
    def setUp(self):
        # Each test will have a different database file created in a temporary
        # directory. The database and the directory containing it is removed at
        # the end of each test.
        self.dir = tempfile.TemporaryDirectory()
        self.app = create_app(DB=path.join(self.dir.name, "test.db"))
        self.app.testing = True

    def tearDown(self):
        self.dir.cleanup()

    def test_index_without_todos(self):
        with self.app.test_client() as client:
            response = client.get("/")
            self.assertIn(b"No to-dos yet!", response.data)

    def test_add_and_complete_todo(self):
        with self.app.test_client() as client:
            item = "This is a test todo"
            response = client.post("/add", follow_redirects=True, data={"item": item})
            self.assertIn(item, response.text)
            response = client.post("/done/1", follow_redirects=True)
            self.assertNotIn(item, response.text)
