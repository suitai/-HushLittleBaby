#!/usr/bin/env python
# -*- coding:utf-8 -*-


import os
import json
from requests_oauthlib import OAuth1Session
from flask import session, request


class Tweet(object):
    def __init__(self):
        self.urls = {
                "request_token": "https://api.twitter.com/oauth/request_token",
                "authenticate": "https://api.twitter.com/oauth/authenticate",
                "access_token": "https://api.twitter.com/oauth/access_token",
                "timeline": "https://api.twitter.com/1.1/statuses/home_timeline.json",
                "search": "https://api.twitter.com/1.1/search/tweets.json",
                "timeline": "https://api.twitter.com/1.1/statuses/home_timeline.json",
                "favorite": "https://api.twitter.com/1.1/favorites/list.json",
                "lists": "https://api.twitter.com/1.1/lists/list.json",
                "list": "https://api.twitter.com/1.1/lists/statuses.json",
                "user": "https://api.twitter.com/1.1/statuses/user_timeline.json",
                "trends": "https://api.twitter.com/1.1/trends/place.json"
                }
        self.woeid = {
                "Japan": 23424856,
                "Tokyo": 1118370,
                "Osaka": 15015370,
                "Nagoya": 1117817
                }
        self.keys = {}
        self.load_environ()

    def load_environ(self):
        self.keys['consumer_key'] = os.environ['CONSUMER_KEY']
        self.keys['consumer_secret'] = os.environ['CONSUMER_SECRET']
        self.keys['callback_url'] = os.environ['CALLBACK_URL']

    def get_redirect_url(self):
        oauth = OAuth1Session(
                self.keys['consumer_key'],
                client_secret=self.keys['consumer_secret'],
                callback_uri=self.keys['callback_url'])
        try:
            oauth.fetch_request_token(self.urls['request_token'])
            return oauth.authorization_url(self.urls['authenticate'])
        except Exception:
            raise

    def set_access_token(self):
        if session.get('access_token') is not None:
            access_token = session.get('access_token')
        else:
            request_token = get_request_token()
            oauth = OAuth1Session(
                    self.keys['consumer_key'],
                    client_secret=self.keys['consumer_secret'],
                    resource_owner_key=request_token['oauth_token'],
                    verifier=request_token['oauth_verifier'])
            try:
                access_token = oauth.fetch_access_token(self.urls['access_token'])
            except Exception:
                raise
            if access_token['oauth_token'] is not None and access_token['oauth_token_secret'] is not None:
                session['access_token'] = access_token
        self.keys['access_token'] = access_token['oauth_token']
        self.keys['access_token_secret'] = access_token['oauth_token_secret']
        print "access_token: ", access_token

    def get_tweets(self, case, params={}):
        oauth = OAuth1Session(
                self.keys['consumer_key'],
                client_secret=self.keys['consumer_secret'],
                resource_owner_key=self.keys['access_token'],
                resource_owner_secret=self.keys['access_token_secret'])
        try:
            res = oauth.get(self.urls[case], params=params)
            return json.loads(res.text)
        except Exception:
            raise


def get_request_token():
    if session.get('request_token') is not None:
        request_token = session.get('request_token')
    else:
        request_token = {
                'oauth_token': request.values.get('oauth_token'),
                'oauth_verifier': request.values.get('oauth_verifier')}
        if request_token['oauth_token'] is not None and request_token['oauth_verifier'] is not None:
            session['request_token'] = request_token
    print "request_token: ", request_token
    return request_token


def check_token():
    if session.get('access_token') is not None:
        return True
    elif session.get('request_token') is not None:
        return True
    else:
        return False


def clean_session():
    for s in ['request_token', 'access_token']:
        session.pop(s, None)


class TweetError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


### Execute
if __name__ == "__main__":
    pass

