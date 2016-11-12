from flask import Flask
from flask import request, redirect
import json
import requests
import urllib

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == 'bear':
            return request.args.get('hub.challenge')
        else:
            return 'Wrong validation token'
    elif request.method == 'POST':
	return 'bleh'
