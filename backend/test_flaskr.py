import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        DATABASE_NAME = "fyuur_test"
        username = 'postgres'
        password = 'bash'
        url = 'localhost:5432'

        self.app = create_app()
        self.client = self.app.test_client
        # self.database_name = "trivia_test"
        self.database_path =  "postgresql://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)
        setup_db(self.app, self.database_path)

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

    
    def test_get_questions(self):
        response = self.client().get('/api/questions')
        self.assertEqual(response.status_code, 200)

    def test_invalid_question_page(self):
        response = self.client().get('/api/questions?page=10000')
        self.assertEqual(response.status_code, 404)


    def test_add_question(self):
        new_question = {
            'question': 'Wetin you wan be for life?',
            'answer': 'I wan be seniorman',
            'difficulty': 1,
            'category': 1
        }
        response = self.client().post('/api/questions', json=new_question)
        self.assertEqual(response.status_code, 200)

    def test_failed_invalid_question(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
        }
        response = self.client().post('/api/questions', json=new_question)
        self.assertEqual(response.status_code, 422)

    def test_search_questions(self):
        new_search = {'searchTerm': 'a'}
        response = self.client().post('/api/questions/search', json=new_search)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_failed_search_question(self):
        new_search = {
            'searchTerm': '',
        }
        response = self.client().post('/api/questions/search', json=new_search)
        self.assertEqual(response.status_code, 404)

    def test_categories(self):
        response = self.client().get('/api/categories')
        self.assertEqual(response.status_code, 200)

    def test_failed_invalid_category(self):
        response = self.client().get('/api/categories/9999')
        self.assertEqual(response.status_code, 404)


    def test_questions_per_category(self):
        response = self.client().get('/api/category/1/questions')
        self.assertEqual(response.status_code, 200)

    def test_failed_questions_per_category(self):
        response = self.client().get('/api/category/a/questions')
        self.assertEqual(response.status_code, 404)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()