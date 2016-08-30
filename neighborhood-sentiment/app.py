"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import json
import os

import boto3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')

dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id=os.environ.get("DYNAMODB_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("DYNAMODB_AWS_SECRET_ACCESS_KEY")
)

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/sentiments/')
def sentiments():
    output = [
        {
            'neighborhood': 'Wall Street',
            'sentiment': .7
        },
        {
            'neighborhood': 'East Village',
            'sentiment': -.7
        }
    ]
    response = dynamodb.scan(TableName='neighborhood_sentiments')
    output = []
    for neighborhood_sentiment in response['Items']:
        formatted = {}
        formatted['neighborhood'] = str(neighborhood_sentiment['neighborhood']['S'])
        formatted['sentiment'] = float(neighborhood_sentiment['sentiment']['N'])
        output.append(formatted)
    print "response['Items']: " + str(response['Items'])
    print "output: " + str(output)
    return json.dumps(output)


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
