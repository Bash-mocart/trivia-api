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
        res = self.client().get('/api/questions')
        data = json.loads(res.data)
        # testing
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_failed_invalid_question_page(self):
        res = self.client().get('/api/questions?page=10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_delete_question(self):
        question = Question(question='new question', answer='new answer',difficulty=1, category=1)
        question.insert()
        question_id = question.id
        res = self.client().delete(f'/api/question/{question_id}')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == question.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)

    def test_failed_deleting_invalid_question(self):
        res = self.client().delete('/api/question/a')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_add_question(self):
        new_question = {
            'question': 'Tell me about yourself?',
            'answer': 'I be seniorman',
            'difficulty': 3,
            'category': 1
        }
        total_questions_before = len(Question.query.all())
        res = self.client().post('/api/questions', json=new_question)
        data = json.loads(res.data)
        total_questions_after = len(Question.query.all())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_questions_after, total_questions_before + 1)

    def test_failed_invalid_question(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        res = self.client().post('/api/questions', json=new_question)
        data = json.loads(res.data)
        #testing
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_questions(self):
        new_search = {'searchTerm': 'a'}
        res = self.client().post('/api/questions/search', json=new_search)
        data = json.loads(res.data)
        # testing
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_failed_search_question(self):
        new_search = {
            'searchTerm': '',
        }
        res = self.client().post('/api/questions/search', json=new_search)
        data = json.loads(res.data)
        #testing
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)
        #testing
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_invalid_category(self):
        res = self.client().get('/api/categories/9999')
        data = json.loads(res.data)
        #testing
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_questions_per_category(self):
        res = self.client().get('/api/category/1/questions')
        data = json.loads(res.data)
        #testing
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_failed_questions_per_category(self):
        res = self.client().get('/api/category/a/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()