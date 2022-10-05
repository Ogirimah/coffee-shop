from crypt import methods
import os
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN AND BEFORE EVERY POSTMAN TEST
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    ''' Query the database for all the drinks and .short() format the result
    '''
    try:
        query_result = Drink.query.all()
        print(query_result)

    except:
        return jsonify({
            'success': False,
            'Message': 'Server Error'
        })
    
    drinks = [drink.short() for drink in query_result]
    # Return json object
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_detailed_drinks(jwt):
    '''Retrieves all drinks from database and .long format the drinks
    '''
    try:
        query_result = Drink.query.all()
        drinks = [drink.long() for drink in query_result]
    except:
        abort(500)

    # Return the formated drinks in json object
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def post_new_drink(jwt):
    # Get new drink from request
    try:
        req = request.get_json()
        title = req.get('title')
        print(title)
        recipe = req.get('recipe')
        print(recipe)
        print('This is being called')
        # Create a drink object with the request
        new_drink = Drink(
                    title=title,
                    recipe=json.dumps(recipe)
                    )
    except:
        abort(422)
    
    # Add the new drink as row in the database
    new_drink.insert()
    drink = new_drink.long()
    return jsonify({
        'success': True,
        'drinks': drink
    }), 200


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def edit_drinks(jwt, id):
    # Error if id is not found
    if id == None:
        abort(404)
    req = request.json
    drink_data = Drink.query.get(id)

    if 'title' in req:
        drink_data.title = req['title']

    if 'recipe' in req:
        drink_data.recipe = req['recipe']

    try:
        drink_data.update()
    except:
        abort(422)
    #  Update database row with new data
    drink = Drink.query.get(id)
    return jsonify({
        'success': True,
        'drinks': [drink_data.long()]
    }), 200


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drinks(jwt, id):
    # Error for <id> not found
    if id == None:
        abort(404)
    try:
        delete_drink = Drink.query.get(id)
    except:
        abort(404)
    delete_drink.delete()
    return jsonify({
        'success': True,
        'delete': id
    }), 200

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422



@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found'
        }), 404


@app.errorhandler(AuthError)
def authentication_and_or_authorization_failure(handle):
    return jsonify({
        'success': False,
        'error': [str(error) for error in handle.args],
    }), handle.status_code

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Server error'
    }), 500