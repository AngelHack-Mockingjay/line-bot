import os
import sys
import requests
import re
import random
import json

from bs4 import BeautifulSoup
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def replyMessage(content):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
    except LineBotApiError as e:
        print (e)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == '拉':
        content = ''
        content += event.message.text + ': pull some message'
        replyMessage(content)
        return 0

    userId = event.source.userId
    payload = {'userId':userId,'userName':'Guest','userMessage':event.message.text,'userPlateform':'line'}
    jsondata = json.dumps(payload, ensure_ascii=False)

    url = 'http://10.187.1.121:14433/message'
    req = res.post(url, params=jsondata)
    print (req)


if __name__ == "__main__":
    app.run()
