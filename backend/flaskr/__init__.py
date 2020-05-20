import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
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

    @app.route('/questions/', methods=['POST', 'GET'])
    def get_questions():
        # getting all the questions
        if request.method == 'GET':
            pagenum = request.args.get('page', 1, int)
            start = (pagenum - 1)
            end = start + QUESTIONS_PER_PAGE
            query = Question.query.all()[start:end]
            questions = [ques.format() for ques in query]
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
                questionsterm = Question.query.\
                    filter(Question.question.like(search)).all()
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
            query = Question.query.filter_by(category=category).all()
            for try_question in query:
                if try_question.id not in previous_questions:
                    question = try_question.format()
                    break

        return jsonify({
            'success': True,
            'question': question
        })

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
