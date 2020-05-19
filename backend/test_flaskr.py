import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from backend.flaskr import create_app
from backend.models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://postgres:123@localhost:5432/trivia_test'
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'what the meaning of the universe',
            'answer': 'potato',
            'category': 2,
            'difficulty': 3
        }
        self.bad_question = {
            'questionww': 'what the meaning of the universe',
            'answerww': 'potato',
            'categoryww': 2,
            'difficultyww': 3
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # creating a new question successfully
    def test_create_new_question(self):
        res = self.client().post('/questions/', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # 422 error code for creating a a question
    def test_422_if_question_creation_fails(self):
        res = self.client().post('/books', json=self.bad_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # deleting a question successfully
    def test_delete_question(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # 404 error code for not finding the question to delete it
    def test_404_delete_question(self):
        res = self.client().delete('/questions/10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
