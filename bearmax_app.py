from flask import Flask
from flask import request, redirect
import json
import requests
import urllib

FB_APP_TOKEN = 'EAAQ7z3BxdYgBAHGNIM6phWb4mH0vDCfsaQaY5rxoN4ZCzZBaKmheZCsYZAkLZCB5XLmcUKkby9N5ncCPIH58swZCp5jRhTTnEQ9aaDttl4eVYUMp8h3x954vUQ6SsX5JOPeEZAhGkdl3ot5jfy8UtgZBDIXWdkOyk51Q13C3ZBoAC2QZDZD'
FB_ENDPOINT = 'https://graph.facebook.com/v2.6/me/{0}'
FB_MESSAGES_ENDPOINT = FB_ENDPOINT.format('messages')
FB_THREAD_SETTINGS_ENDPOINT = FB_ENDPOINT.format('thread_settings')

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
        data = json.loads(request.data)['entry'][0]['messaging']
	for i in range(len(data)):
	    event = data[i]
	    if 'sender' in event:
		sender_id = event['sender']['id']
		send_FB_message(sender_id, 'bearmax')




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
