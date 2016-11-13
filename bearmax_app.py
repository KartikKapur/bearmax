from flask import Flask
from flask import request, redirect
import json
import requests
import urllib
from webob import Response

from pymongo import MongoClient

import watson

from symptomchecker import SymptomChecker

FB_APP_TOKEN = 'EAAQ7z3BxdYgBAL3ZBOmSKkUZCS9NodoMynT2SGZCZCjEo671spa5qVwGkhTVLZBofZAtgxQJc4RIbp9aHbOVesY5jDZC6oKgr8bqzkO6ewklEDM2xC12gLDuEkmeXQNEDBPDQ4mtWY8yRp2uEc77rR0wRCGNIPV66Q4sicfKgMuVAZDZD' 
FB_ENDPOINT = 'https://graph.facebook.com/v2.6/me/{0}'
FB_MESSAGES_ENDPOINT = FB_ENDPOINT.format('messages')
FB_THREAD_SETTINGS_ENDPOINT = FB_ENDPOINT.format('thread_settings')

MONGO_DB_BEARMAX_DATABASE = 'bearmax'
MONGO_DB_BEARMAX_ENDPOINT = 'ds151707.mlab.com'
MONGO_DB_BEARMAX_PORT = 51707

MONGO_DB_USERNAME = 'bearmax'
MONGO_DB_PASSWORD = 'calhacks'

SYMPTOMS_THRESHOLD = 4

def connect():
    connection = MongoClient(
        MONGO_DB_BEARMAX_ENDPOINT,
        MONGO_DB_BEARMAX_PORT
    )
    handle = connection[MONGO_DB_BEARMAX_DATABASE]
    handle.authenticate(
        MONGO_DB_USERNAME,
        MONGO_DB_PASSWORD
    )
    return handle

app = Flask(__name__)
app.config['DEBUG'] = True
handle = connect()

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == 'bear':
            return request.args.get('hub.challenge')
        else:
            return 'Wrong validation token'
    elif request.method == 'POST':
        data = json.loads(request.data)['entry'][0]['messaging']
        for i in range(len(data)):
            event = data[i]
            if 'sender' in event:
                print('Event: {0}'.format(event))
                sender_id = event['sender']['id']
                if 'message' in event and 'is_echo' in event['message'] and event['message']['is_echo']:
                    pass
                elif handle.bot_users.find({'sender_id': sender_id}).count() == 0:
                    send_FB_text(sender_id, 'Hello. I am Bearmax, your personal healthcare assistant.')
                    init_bot_user(sender_id)
                else:
                    sender_id_matches = [x for x in handle.bot_users.find({'sender_id': sender_id})]
                    if sender_id_matches:
                        bot_user = sender_id_matches[0]
                        apimedic_client = SymptomChecker()
                        handle_event(event, bot_user, apimedic_client)

    return Response()

def handle_event(event, bot_user, apimedic_client):
    if 'message' in event and 'text' in event['message']:
        message = event['message']['text']
        print('Message: {0}'.format(message))
        if 'Gender:' and 'YOB:' in message:
            gender_string, yob_string = message.split(',')
            gender, yob = gender_string.split(': ')[1], int(yob_string.split(': ')[1])
            init_gender_yob(bot_user['sender_id'], gender, yob)
            send_FB_text(bot_user['sender_id'], 'Thank you.')
        elif 'quick_reply' in event['message']:
            handle_quick_replies(
                event['message']['quick_reply']['payload'],
                bot_user,
                apimedic_client
            )
        else:
            natural_language_classifier, instance_id = watson.init_nat_lang_classifier(True)
            symptom, symptom_classes = watson.get_symptoms(message, natural_language_classifier, instance_id)
            print('Symptom: {0}, Symptom Classes: {1}'.format(symptom, symptom_classes))
            symptom_classes = ','.join([symptom_class['class_name'] for symptom_class in symptom_classes])
            send_FB_text(
                bot_user['sender_id'],
                'You seem to have {0}. Is this true?'.format(symptom),
                quick_replies=yes_no_quick_replies(symptom, symptom_classes)
            )

def diagnose(apimedic_client, bot_user):
    diagnosis = apimedic_client.get_diagnosis(
        bot_user['symptoms'],
        bot_user['gender'],
        bot_user['year_of_birth']
    )
    for diag in diagnosis:
        name, specialisation = diag['Issue']['Name'], diag['Specialisation'][0]['Name']
        accuracy = diag['Issue']['Accuracy']
        # if specialisation == 'General practice':
        #     specialisation_msg = 'You shouldn\'t worry. Just take rest and drink lots of fluids!'
        send_FB_text(bot_user['sender_id'], 'You have a {0}% chance of {1}'.format(accuracy, name))
    send_FB_text(bot_user['sender_id'], 'You should seek {0} for your {1}'.format(specialisation, name))
    reset_symptoms(bot_user)



def handle_quick_replies(payload, bot_user, apimedic_client):
    print('Payload: {0}'.format(payload))
    if 'Yes:' in payload:
        add_symptom(bot_user, payload.split(':')[1])
        bot_user = [x for x in handle.bot_users.find({'sender_id': bot_user['sender_id']})][0]
        if len(bot_user['symptoms']) >= SYMPTOMS_THRESHOLD:
            diagnose(apimedic_client, bot_user)
        else:
            proposed_symptoms = apimedic_client.get_proposed_symptoms(
                bot_user['symptoms'],
                bot_user['gender'],
                bot_user['year_of_birth']
            )
            symptom_names = [symptom['Name'] for symptom in proposed_symptoms if symptom['Name'] not in bot_user['symptoms_seen']]
            symptom, symptom_classes = symptom_names[0], ','.join(symptom_names)

            send_FB_text(
                bot_user['sender_id'],
                'Alright. Do you also have {0}?'.format(symptom),
                quick_replies=yes_no_quick_replies(symptom, symptom_classes)
            )
    elif 'No:' in payload:
        symptom_classes = payload.split(':')[1].split(',')
        add_symptom_seen(bot_user, symptom_classes.pop(0))
        if symptom_classes == ['']:
            if bot_user['symptoms']:
               diagnose(apimedic_client, bot_user) 
            else:
                send_FB_text(
                    bot_user['sender_id'],
                    'I\'m sorry, but I was not able to diagnose you.'
                )
        else:
            symptom, symptom_classes = symptom_classes[0], ','.join(symptom_classes)
            send_FB_text(
                bot_user['sender_id'],
                'Alright. Do you have {0}?'.format(symptom),
                quick_replies=yes_no_quick_replies(symptom, symptom_classes)
            )


def yes_no_quick_replies(symptom, symptom_classes):
    return [
        {
            'content_type': 'text',
            'title': 'Yes',
            'payload': 'Yes:{0}'.format(symptom)
        },
        {
            'content_type': 'text',
            'title': 'No',
            'payload': 'No:{0}'.format(symptom_classes)
        }
    ]


def add_symptom(bot_user, symptom):
    handle.bot_users.update(
        {'sender_id': bot_user['sender_id']},
        {
            '$set': {
                'symptoms': bot_user['symptoms'] + [symptom]
            }
        }
    )


def add_symptom_seen(bot_user, symptom):
    handle.bot_users.update(
        {'sender_id': bot_user['sender_id']},
        {
            '$set': {
                'symptoms_seen': bot_user['symptoms_seen'] + [symptom]
            }
        }
    )

def reset_symptoms(bot_user):
    handle.bot_users.update(
        {'sender_id': bot_user['sender_id']},
        {
            '$set': {
                'symptoms': [],
                'symptoms_seen': []
            }
        }
    )

def init_bot_user(sender_id):
    send_FB_text(sender_id, 'Please enter your gender and your year of birth as follows: \"Gender: <gender>, YOB: <yob>\"')
    handle.bot_users.insert({
        'sender_id': sender_id,
        'symptoms': [],
        'symptoms_seen': []
    })

def init_gender_yob(sender_id, gender, yob):
    handle.bot_users.update(
        {'sender_id': sender_id},
        {
            '$set': {
                'gender': gender,
                'year_of_birth': yob
            }
        }
    )

def send_FB_message(sender_id, message):
    fb_response = requests.post(
        FB_MESSAGES_ENDPOINT,
        params={'access_token': FB_APP_TOKEN},
        data=json.dumps(
            {
                'recipient': {
                    'id': sender_id
                },
                'message': message
            }
        ),
        headers={'content-type': 'application/json'}
    )
    if not fb_response.ok:
        app.logger.warning('Not OK: {0}: {1}'.format(
            fb_response.status_code,
            fb_response.text
        ))


def send_FB_text(sender_id, text, quick_replies=None):
    message = {'text': text}
    if quick_replies:
        message['quick_replies'] = quick_replies
    return send_FB_message(
        sender_id,
        message
    )


def send_FB_buttons(sender_id, text, buttons):
    return send_FB_message(
        sender_id,
        {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': text,
                    'buttons': buttons
                }
            }
        }
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
