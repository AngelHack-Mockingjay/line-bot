#!/usr/bin/env python3
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

server_host = 'https://c1d0f3dc.ngrok.io'

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

def getPullContentToString(jd,userId):
    content = ''
    for d in jd['messageList']:
        userName = jd['userObject'][d['userID']]['userName']
        print (userName, d['userMessage'], d['userPlatform'])
        strs =  "({})說：{} (來自{})\n".format(userName,d['userMessage'],d['userPlatform'])
        print (strs)
        content = content + strs
    return content

def getFilteredMessage(userId, data):
    new_data = []
    try:
        myUpdatedAt = data['userObject'][userId]['userUpdatedAt']
        for message in data['messageList']:
            messageCreatedOn = message['createdOn']
            if myUpdatedAt < messageCreatedOn:
                # add
                print ('add ', message)
                new_data.append(message)
        data['messageList'] = new_data
    except KeyError as e:
        print (e)
    return data

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print (event)
    userId = event.source.user_id

    print (event.message.text)

    if event.message.text.find('哈哈') > -1:
        # get message
        url = server_host + '/message/list'
        req = requests.get(url)
        data = req.json()
        filteredData = getFilteredMessage(userId, data)
        replyMessage(event, getPullContentToString(filteredData,userId))

        # update time
        url2 = server_host + '/message/user/update'
        payload2 = {'userID': userId, 'userPlatform': 'line'}
        req2 = requests.post(url2, json=payload2)

        payload = {'userID':userId, 'userName':'Guest', 'userMessage':event.message.text, 'userPlateform':'line'}
        url = server_host + '/message'
        req = requests.post(url, json=payload)

        return 0

    payload = {'userID':userId, 'userName':'Guest', 'userMessage':event.message.text, 'userPlateform':'line'}
    url = server_host + '/message'
    req = requests.post(url, json=payload)

    # update time
    url2 = server_host + '/message/user/update'
    payload2 = {'userID': userId, 'userPlatform': 'line'}
    req2 = requests.post(url2, json=payload2)


if __name__ == "__main__":
    app.run()
