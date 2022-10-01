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
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    ''' Query the database for all the drinks and .short() format the result
    '''
    try:
        query_result = Drink.query.all()
        print(query_result)
        drinks = [drink.short() for drink in query_result]

    except:
        return jsonify({
            'success': False,
            'Message': 'Server Error'
        })
    
    # Return json object
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@requires_auth(permission='get:drinks-detail')
@app.route('/drinks-detail')
def get_detailed_drinks():
    '''Retrieves all drinks from database and .long format the drinks
    '''
    try:
        # Retrieve all drinks
        query_result = Drink.query.all()
        # .long format the drinks
        drinks = [drink.long() for drink in query_result]
    except:
        abort(500)

    # Return the formated drinks in json object
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@requires_auth(permission='post:drinks')
@app.route('/drinks', methods=['POST'])
def post_new_drink():
    # Get new drink from request
    try:
        req = request.json
        print(req)
        # Create a drink object with the request
        new_drink = Drink(
                    id=req['id'],
                    title=req['title'],
                    recipe=req['recipe']
                    )
    except:
        abort(422)
    
    # Add the new drink as row in the database
    new_drink.insert()
    drink = Drink.query.filter(id=new_drink[id]).all()
    return jsonify({
        'success': True,
        'drinks': drink.long()
    }), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@requires_auth(permission='patch:drinks')
@app.route('/drinks/<id>', methods=['PATCH'])
def edit_drinks(id):
    # Error if id is not found
    if id == None:
        abort(404)
    try:
        req = request.json
        print(req)
        drink_data = Drink(
            id = id,
            title = req['title'],
            recipe = req['recipe']
            )
    except:
        abort(422)
    #  Update database row with new data
    drink_data.update()
    drink = Drink.query.filter(id=id).all()
    return jsonify({
        'success': True,
        'drink': drink.long()
    }), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@requires_auth(permission='delete:drinks')
@app.route('/drinks/<id>', methods=['DELETE'])
def delete_drinks(id):
    # Error for <id> not found
    if id == None:
        abort(404)
    try:
        delete_drink = Drink.query.filter(id=id).all()
        delete_drink.delete()
    except:
        abort(500)
    return jsonify({
        'success': True,
        'delete': id
    }), 200



# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found'
        }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_and_or_authorization_failure(handle):
    return jsonify(handle.error), handle.status_code

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': True,
        'error': 500,
        'message': 'Server error'
    })