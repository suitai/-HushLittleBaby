#!/usr/bin/env python
# -*- coding:utf-8 -*-


import os
import json
import logging
from requests_oauthlib import OAuth1Session, OAuth2Session, oauth1_session
from oauthlib.oauth2 import BackendApplicationClient

logger = logging.getLogger()

KEYS = {
    'consumer_key': os.environ['CONSUMER_KEY'],
    'consumer_secret': os.environ['CONSUMER_SECRET'],
    'callback_url': os.environ['CALLBACK_URL']
}

URLS = {
    'oauth': {
        "request_token": "https://api.twitter.com/oauth/request_token",
        "authenticate": "https://api.twitter.com/oauth/authenticate",
        "access_token": "https://api.twitter.com/oauth/access_token",
        "oauth2_token": "https://api.twitter.com/oauth2/token"
        },
    'get': {
        "search": "https://api.twitter.com/1.1/search/tweets.json",
        "home_timeline": "https://api.twitter.com/1.1/statuses/home_timeline.json",
        "favorites": "https://api.twitter.com/1.1/favorites/list.json",
        "lists": "https://api.twitter.com/1.1/lists/list.json",
        "friends": "https://api.twitter.com/1.1/friends/list.json",
        "list_status": "https://api.twitter.com/1.1/lists/statuses.json",
        "user_timeline": "https://api.twitter.com/1.1/statuses/user_timeline.json",
        "trends": "https://api.twitter.com/1.1/trends/place.json"
    },
    'post': {
        "favorite-create": "https://api.twitter.com/1.1/favorites/create.json",
        "favorite-destroy": "https://api.twitter.com/1.1/favorites/destroy.json",
        "retweet": "https://api.twitter.com/1.1/statuses/retweet/{0}.json",
        "unretweet": "https://api.twitter.com/1.1/statuses/unretweet/{0}.json"
    }
}


def get_tweet_url(twtype, params={}):
    if twtype in ['retweet', 'unretweet']:
        url = URLS['post'][twtype].format(params['id'])
        method = "post"
    elif twtype in URLS['post'].keys():
        url = URLS['post'][twtype]
        method = "post"
    elif twtype in URLS['get'].keys():
        url = URLS['get'][twtype]
        method = "get"

    return url, method


def get_tweets(access_token, twtype, params={}, ):
    oauth = OAuth1Session(KEYS['consumer_key'],
                client_secret=KEYS['consumer_secret'],
                resource_owner_key=access_token['oauth_token'],
                resource_owner_secret=access_token['oauth_token_secret'])

    url, method = get_tweet_url(twtype, params)

    try:
        if method == "get":
            res = oauth.get(url, params=params)
        elif method == "post":
            res = oauth.post(url, params=params)

        result = json.loads(res.text)

    except oauth1_session.TokenRequestDenied as detail:
        logger.error(detail)
        raise RequestDenied(detail)
    except (ValueError, TypeError) as detail:
        logger.error(res.text)
        raise RequestDenied(detail)

    return result


def get_redirect_url():
    url = None
    oauth = OAuth1Session(KEYS['consumer_key'],
                client_secret=KEYS['consumer_secret'],
                callback_uri=KEYS['callback_url'])
    try:
        oauth.fetch_request_token(URLS['oauth']['request_token'])
        url =  oauth.authorization_url(URLS['oauth']['authenticate'])
    except oauth1_session.TokenRequestDenied as detail:
        raise RequestDenied(detail)
    return url


def get_access_token(request_token):
    oauth = OAuth1Session(KEYS['consumer_key'],
                client_secret=KEYS['consumer_secret'],
                resource_owner_key=request_token['oauth_token'],
                verifier=request_token['oauth_verifier'])
    try:
        access_token = oauth.fetch_access_token(URLS['oauth']['access_token'])
    except oauth1_session.TokenRequestDenied as detail:
        raise RequestDenied(detail)

    logger.debug("access_token: {}".format(access_token))
    return access_token


class RequestDenied(Exception):
    pass


### Execute
if __name__ == "__main__":
    pass

