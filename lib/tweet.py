#!/usr/bin/env python
# -*- coding:utf-8 -*-


import os
import json
from requests_oauthlib import OAuth1Session, oauth1_session
from flask import session, request

KEYS = {}
KEYS['consumer_key'] = os.environ['CONSUMER_KEY']
KEYS['consumer_secret'] = os.environ['CONSUMER_SECRET']
KEYS['callback_url'] = os.environ['CALLBACK_URL']

URLS = {}
URLS['oauth'] = {
        "request_token": "https://api.twitter.com/oauth/request_token",
        "authenticate": "https://api.twitter.com/oauth/authenticate",
        "access_token": "https://api.twitter.com/oauth/access_token",
        "oauth2_token": "https://api.twitter.com/oauth2/token",
        }
URLS['get'] = {
        "search": "https://api.twitter.com/1.1/search/tweets.json",
        "home_timeline": "https://api.twitter.com/1.1/statuses/home_timeline.json",
        "favorites": "https://api.twitter.com/1.1/favorites/list.json",
        "lists": "https://api.twitter.com/1.1/lists/list.json",
        "list_status": "https://api.twitter.com/1.1/lists/statuses.json",
        "user_timeline": "https://api.twitter.com/1.1/statuses/user_timeline.json",
        "trends": "https://api.twitter.com/1.1/trends/place.json"
        }
URLS['post'] = {
        "favorite-create": "https://api.twitter.com/1.1/favorites/create.json",
        "favorite-destroy": "https://api.twitter.com/1.1/favorites/destroy.json",
        "retweet": "https://api.twitter.com/1.1/statuses/retweet/",
        "unretweet": "https://api.twitter.com/1.1/statuses/unretweet/"
        }

class Tweet(object):
    def __init__(self):
        self.token = {}
        self.set_access_token()
        self.set_oauth()

    def set_access_token(self):
        access_token = get_access_token()
        self.token['access_token'] = access_token['oauth_token']
        self.token['access_token_secret'] = access_token['oauth_token_secret']

    def set_oauth(self):
        self.oauth = OAuth1Session(
                KEYS['consumer_key'],
                client_secret=KEYS['consumer_secret'],
                resource_owner_key=self.token['access_token'],
                resource_owner_secret=self.token['access_token_secret'])

    def get_tweets(self, twtype, params={}):
        if twtype in ['retweet', 'unretweet']:
            url = URLS['post'][twtype] + params['id'] + ".json"
            method = "post"
        elif twtype in URLS['post'].keys():
            url = URLS['post'][twtype]
            method = "post"
        elif twtype in URLS['get'].keys():
            url = URLS['get'][twtype]
            method = "get"

        try:
            if method == "get":
                res = self.oauth.get(url, params=params)
            elif method == "post":
                res = self.oauth.post(url, params=params)
            return json.loads(res.text)

        except oauth1_session.TokenRequestDenied as detail:
            print detail
            raise RequestDenied(detail)

        except ValueError as detail:
            print "response:", res.text
            return None


def get_redirect_url():
    oauth = OAuth1Session(
            KEYS['consumer_key'],
            client_secret=KEYS['consumer_secret'],
            callback_uri=KEYS['callback_url'])
    try:
        oauth.fetch_request_token(URLS['oauth']['request_token'])
        return oauth.authorization_url(URLS['oauth']['authenticate'])
    except oauth1_session.TokenRequestDenied as detail:
        clean_session()
        raise RequestDenied(detail)


def get_request_token():
    if session.get('request_token') is not None:
        request_token = session.get('request_token')
    else:
        request_token = {
                'oauth_token': request.values.get('oauth_token'),
                'oauth_verifier': request.values.get('oauth_verifier')}
        if request_token['oauth_token'] is not None and request_token['oauth_verifier'] is not None:
            session['request_token'] = request_token
    print "request_token:", request_token
    return request_token


def get_access_token():
    if session.get('access_token') is not None:
        access_token = session.get('access_token')
    else:
        request_token = get_request_token()
        oauth = OAuth1Session(
                KEYS['consumer_key'],
                client_secret=KEYS['consumer_secret'],
                resource_owner_key=request_token['oauth_token'],
                verifier=request_token['oauth_verifier'])
        try:
            access_token = oauth.fetch_access_token(URLS['oauth']['access_token'])
        except oauth1_session.TokenRequestDenied as detail:
            clean_session()
            raise RequestDenied(detail)

        if access_token['oauth_token'] is not None and access_token['oauth_token_secret'] is not None:
            session['access_token'] = access_token
    print "access_token:", access_token
    return access_token


def check_token():
    if session.get('access_token') is not None:
        return True
    elif session.get('request_token') is not None:
        return True
    else:
        request_token = get_request_token()
        if request_token['oauth_token'] is not None and request_token['oauth_verifier'] is not None:
            return True
        return False


def clean_session():
    for s in ['request_token', 'access_token']:
        session.pop(s, None)


class RequestDenied(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


### Execute
if __name__ == "__main__":
    pass

