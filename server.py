import requests
from flask import Flask, request
from dbfunction import DatabaseConnection, EvaluationFunction
from sns_sub import SnsWrapper
import logging
import boto3
from botocore.exceptions import ClientError

host = 'lioncoursedatabase.c5zzynku9kw4.us-east-2.rds.amazonaws.com'
database_user_id = 'LionCourseAdmin'
database_user_password = 'Rivendell'
default_scheme = '6156_Project'

def create_cursor(host = host, database_user_id = database_user_id, database_user_password = database_user_password, default_scheme = default_scheme):
    db = DatabaseConnection(host, database_user_id, database_user_password, default_scheme)
    cur, conn = db.connection()
    return cur, conn

master_url = 'https://www.lioncourse.org:5000'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Rivendell'

@app.route('/rating/<search_key>', methods=['GET'])
def get_rating(search_key):
    try:
        cur, conn = create_cursor()
        search_engine = EvaluationFunction(default_scheme, cur, conn)
        json_out = search_engine.evaluation_search(search_key)
        return json_out
    except:
        return None 

@app.route('/rating/<search_key>/<update_statement>', methods=['POST'])
def update_rating(search_key, update_statement):
    try:
        cur, conn = create_cursor()
        new_evaluation = update_statement.split('&')
        new_evaluation = [int(score) for score in new_evaluation]
        search_engine = EvaluationFunction(default_scheme, cur, conn)
        search_engine.evaluate(search_key, new_evaluation)
        # SNS
        # email_address = 'jt3302@columbia.edu'
        email_address = requests.get(master_url+"/getEmail").content.decode('UTF-8')
        msg = "Hello! Thanks for evaluating the course. Have a good one!."
        sns_wrapper = SnsWrapper()
        sns_wrapper.subscribe('email', email_address)
        sns_wrapper.publish_msg(msg)
        return 'Update successed.'
    except:
        return 'Update failed.'

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5000)