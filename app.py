#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import logging
import json
from requests_oauthlib import OAuth1Session
from flask import Flask, session, request, redirect, render_template


CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
CALLBACK_URL = os.environ['CALLBACK_URL']
ACS_TOKEN = "acs_token"
URL= {
'request_token': "https://api.twitter.com/oauth/request_token",
'authenticate': "https://api.twitter.com/oauth/authenticate",
'access_token': "https://api.twitter.com/oauth/access_token",
'timeline': "https://api.twitter.com/1.1/statuses/home_timeline.json",
}


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


@app.before_request
def before_request():
    print "INFO: before_request"
    if request.path == '/login':
        return
    if request.path[-4:] == ".css":
        return
    if request.path[-3:] == ".js":
        return
    if session.get(ACS_TOKEN) is not None:
        return
    token =  __get_token()
    if token['oauth_token'] is not None and token['oauth_verifier'] is not None:
        return
    return redirect('/login')


@app.route('/login', methods=['GET'])
def login():
    print "INFO: login"
    redirect_url = __get_redirect_url()
    print "redirect_url: ", redirect_url
    return redirect(redirect_url)


@app.route("/")
def index():
    print "INFO: index"
    token =  __get_token()
    print "token: ", token
    access_token = __get_access_token(token)
    print "access_token: ", access_token
    tweet = __get_tweet(access_token, "timeline")
    return render_template('index.html', timeline=tweet)


def __get_token():
    token = {
            'oauth_token': request.values.get('oauth_token'),
            'oauth_token_secret': request.values.get('oauth_token_secret'),
            'oauth_verifier': request.values.get('oauth_verifier'),
            }
    return token


def __get_redirect_url():
    auth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET,
            callback_uri=CALLBACK_URL)
    try:
        request_token = auth.fetch_request_token(URL['request_token'])
        redirect_url =  auth.authorization_url(URL['authenticate'])
    except Exception:
        raise
    return redirect_url


def __get_access_token(token):
    if session.get(ACS_TOKEN):
        return session.get(ACS_TOKEN)

    auth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET,
            resource_owner_key=token['oauth_token'],
            verifier=token['oauth_verifier'])
    try:
        access_token = auth.fetch_access_token(URL['access_token'])
    except Exception:
        raise

    session[ACS_TOKEN] = access_token
    return access_token


def __get_tweet(token, case, params={}):
    auth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET,
            resource_owner_key=token['oauth_token'],
            resource_owner_secret=token['oauth_token_secret'])
    res = auth.get(URL[case], params=params)
    return json.loads(res.text)


if __name__ == "__main__":
    app.debug = True
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.run(threaded=True)
