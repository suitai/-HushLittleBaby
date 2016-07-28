#!/usr/bin/env python
# -*- coding:utf-8 -*-


import os
import json
from requests_oauthlib import OAuth1Session, oauth1_session
from flask import session, request


class Tweet(object):
    def __init__(self, filename):
        self.urls = {}
        self.woeids = {}
        self.keys = {}
        self.load_config(filename)
        self.load_environ()

    def load_config(self, filename):
        with open(filename, 'r') as f:
            config = json.load(f)
        self.urls = config['urls']
        self.woeids = config['woeids']
        print "INFO: load_config"

    def load_environ(self):
        self.keys['consumer_key'] = os.environ['CONSUMER_KEY']
        self.keys['consumer_secret'] = os.environ['CONSUMER_SECRET']
        self.keys['callback_url'] = os.environ['CALLBACK_URL']
        print "INFO: load_keys"

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
            except oauth1_session.TokenRequestDenied as detail:
                raise RequestDenied(detail)

            if access_token['oauth_token'] is not None and access_token['oauth_token_secret'] is not None:
                session['access_token'] = access_token

        self.keys['access_token'] = access_token['oauth_token']
        self.keys['access_token_secret'] = access_token['oauth_token_secret']
        print "access_token:", access_token

    def get_tweets(self, case, params={}):
        oauth = OAuth1Session(
                self.keys['consumer_key'],
                client_secret=self.keys['consumer_secret'],
                resource_owner_key=self.keys['access_token'],
                resource_owner_secret=self.keys['access_token_secret'])
        try:
            res = oauth.get(self.urls[case], params=params)
            return json.loads(res.text)
        except oauth1_session.TokenRequestDenied as detail:
            print detail
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

