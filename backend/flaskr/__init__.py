import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={r"/*": {"origins": "*"}})
    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        categories = {}
        for cat in Category.query.all():
            categories.update({
                cat.id: cat.type
            })
        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories
        })

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''

    @app.route('/questions/', methods=['POST', 'GET'])
    def get_questions():
        # getting all the questions
        if request.method == 'GET':
            pagenum = request.args.get('page', 1, int)
            start = (pagenum - 1)
            end = start + QUESTIONS_PER_PAGE
            questions = [ques.format() for ques in Question.query.all()[start:end]]
            categories = {}
            for cat in Category.query.all():
                categories.update({
                    cat.id: cat.type
                })
            if len(questions) == 0 or len(categories) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': questions,
                'totalQuestions': len(Question.query.all()),
                'categories': categories,
                'currentCategory': 'ALL'
            })
        # post request it may be a search or post new question
        else:
            data = request.get_json()
            # if its a search:
            if data.get('searchTerm', None) is not None:
                search = f'%{data.get("searchTerm")}%'
                questionsterm = Question.query.filter(Question.question.like(search)).all()
                questions = [ques.format() for ques in questionsterm]
                print('term', search)
                print('result', questions)
                return jsonify({
                    'success': True,
                    'questions': questions,
                    'totalQuestions': len(Question.query.all()),
                    'currentCategory': 'ALL'
                })
            # if its to post a new question
            else:
                try:
                    question = Question(question=data['question'],
                                        answer=data['answer'],
                                        difficulty=data['difficulty'],
                                        category=data['category'])
                    question.insert()
                    return jsonify({
                        'success': True
                    })
                except:
                    abort(422)

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
    
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

    @app.route('/questions/<id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.get(id)
            question.delete()
            if Question.query.get(id) is None:
                return jsonify({
                    'success': True
                })
            else:
                abort(422)
        except:
            abort(404)

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
    
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
    
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    @app.route('/categories/<id>/questions')
    def get_questions_by_category(id):
        try:
            questionscat = Question.query.filter_by(category=id).all()
            questions = [ques.format() for ques in questionscat]

            if len(questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': questions,
                'totalQuestions': len(Question.query.all()),
                'currentCategory': Category.query.get(id).type
            })
        except:
            abort(400)

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
    
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        data = request.get_json()
        previous_questions = data.get('previous_questions')
        category = data.get('quiz_category').get('id')
        # if the player didn't chose a certain category
        question = None
        if category == 0:
            for try_question in Question.query.all():
                if try_question.id not in previous_questions:
                    question = try_question.format()
                    break
        # if the player chose a certain category
        else:
            for try_question in Question.query.filter_by(category=category).all():
                if try_question.id not in previous_questions:
                    question = try_question.format()
                    break

        return jsonify({
            'success': True,
            'question': question
        })

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    @app.errorhandler
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
