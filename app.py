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
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

server_host = 'https://32962999.ngrok.io'

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

def replyMessage(event, content):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
    except LineBotApiError as e:
        print (e)

def getPullContentToString(jd):
    content = ''
    for d in jd:
        strs =  "({})說：{} (來自{})\n".format(d['userName'],d['userMessage'],d['userPlatform'])
        print (strs)
        content = content + strs
    return content

def filterData(userId, data):
    result = {}
    for d in data['messageList']:
        print (d)
        if d['createdOn'] > d.['userObject'][userId]['userUpdatedAt']:
            result.append(d)
    return result

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print (event)
    userId = event.source.user_id

    print (event.message.text)

    if event.message.text == '哈哈':
        # get message
        url = server_host + '/message/list'
        req = requests.get(url)
        data = req.json()
        print (data)
        n = json.dumps(data)
        o = json.loads(n)
        filteredData = filterData(userId, o)
        replyMessage(event, getPullContentToString(filteredData))

        # update time
        url2 = server_host + '/message/user/update'
        payload2 = {'userID': userId, 'userPlatform': 'line'}
        req2 = requests.post(url2, json=payload2)
        return 0

    payload = {'userID':userId, 'userName':'Guest', 'userMessage':event.message.text, 'userPlateform':'line'}
    url = server_host + '/message'
    req = requests.post(url, json=payload)


if __name__ == "__main__":
    app.run()
