import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.operators import ilike_op

from sqlalchemy import null

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 5
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions\

def get_random(questions):
    limit = len(questions)
    
    if limit > 0:
        random_que = random.randint(0, limit - 1)
        questions = questions[random_que].format()
    else: 
        None
    return questions


# db = SQLAlchemy(app)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
   
    # app = Flask(__name__, instance_relative_config=True)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/api/categories')
    def categories():
        categories = Category.query.order_by(Category.type).all()
        if len(categories) == 0:
            abort(404)
        return jsonify({
        'success': True,
        'categories':{category.id: category.type for category in categories}
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/api/questions')
    def questions():
            # Implement pagination
        questions = Question.query.all() 
        ques_by_page = paginate_questions(request, questions)
        categories =  Category.query.all()

        if not ques_by_page:
            abort (404)
        
        return jsonify({
            'success': True,
            'questions':ques_by_page,
            'total_questions':len(questions),
            'categories': {category.id : category.type for category in categories}
        })

        


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/api/question/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/api/questions", methods=['POST'])
    def post_question():
        body = request.get_json()
        try:
            answer =  body["answer"]
            category = body["category"]
            difficulty = body['difficulty']
            question = body["question"]
       
            new_question = Question(question, answer, category, difficulty)
            new_question.insert()
            id = new_question.id

            return jsonify({
                'success': True,
                'created': id,
            })

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/api/questions/search', methods=['POST'])
    def search_questions():
        question_list = []
        body = request.get_json()
        search = body['searchTerm']
  
        search_results = Question.query.filter(ilike_op(Question.question, f'%{search}%')).all() 
        que_by_page = paginate_questions(request, search_results)
        for que in que_by_page:
            question_list.append(que)
        total_questions = len(search_results)

        if not search:
            abort(404)

        return jsonify({
            'success': True,
            'questions': question_list,
            'total_questions': total_questions,
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/api/category/<int:category_id>/questions')
    def que_by_category(category_id):
    
        questions = Question.query.filter(
            Question.category == str(category_id)).all()
        paginate = paginate_questions(request, questions)
        que_by_page = []
        for que in paginate:
            que_by_page.append(que)

        if not questions:
            abort(404)

        return jsonify({
            'success': True,
            'questions': que_by_page,
            'total_questions': len(questions),
            'current_category': category_id
        })

      

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/api/quizzes', methods=['POST'])
    def play_quiz():

        body = request.get_json()
        category = body['quiz_category']
        prev = body['previous_questions']
        type = category["type"]
        id = category["id"]
        not_prev = Question.id.notin_((prev))
        if type == 'click':
            questions = Question.query.filter(not_prev).all()
        else:
            questions = Question.query.filter_by(category=id).filter(not_prev).all()
        question = get_random(questions)
        if questions is None:
            return jsonify({
                'success': True,
           }) 

        if not category:
            abort(404)

        return jsonify({
            'success': True,
            'question': question
        })


            

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422


    return app
