#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import logging
import json
from datetime import timedelta
from flask import Flask, session, request, redirect, render_template, flash, jsonify
from flask_assets import Environment, Bundle
from lib import tweet

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('scss/style.scss', filters='pyscss', output='css/style.css')
assets.register('style_scss', scss)


class TweetError(Exception):
    pass


@app.before_request
def before_request():
    if request.path == '/login':
        return
    elif request.path == '/logout':
        return
    elif request.path[-4:] == ".css":
        return
    elif request.path[-3:] == ".js":
        return
    elif check_token():
        return
    else:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)
        return redirect('/login')


@app.route('/login', methods=['GET'])
def login():
    try:
        redirect_url = tweet.get_redirect_url()
    except tweet.RequestDenied as detail:
        app.logger.error(detail)
        clean_session()
        raise
    app.logger.debug("redirect url: {}".format(redirect_url))
    return redirect(redirect_url)


@app.route('/logout', methods=['GET'])
def logout():
    clean_session()
    return redirect('/login')


@app.route('/', methods=['GET'])
def index():
    request_token = get_request_token()
    access_token = get_access_token(request_token)
    return render_template('index.html', screen_name=access_token['screen_name'])


@app.route('/_get_ipaddr')
def get_ipaddr():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    app.logger.info("ipaddr: {}".format(ip))
    return jsonify({'ip': ip})


@app.route('/_get_tweets', methods=['POST'])
def _get_tweets():
    app.logger.debug("_get_tweets request: {}".format(request.json))
    request_token = get_request_token()
    access_token = get_access_token(request_token)
    try:
        tweets = tweet.get_tweets(access_token, request.json['twtype'], request.json['params'])
        check_tweets(tweets)
        app.logger.debug("tweets num: {}".format(len(tweets)))
        return render_tweets(request.json, tweets)

    except tweet.RequestDenied as detail:
        app.logger.error(detail)
        return redirect('/logout')

    except TweetError as detail:
        app.logger.error(detail)
        return render_template('error.html', message=detail)


@app.route('/_post_tweets', methods=['POST'])
def _post_tweets():
    app.logger.debug("_post_tweets request: {}".format(request.json))
    try:
        tweets = tweet.get_tweets(request.json['twtype'], request.json['params'])
    except tweet.RequestDenied as detail:
        app.logger.error(detail)
        return redirect('/logout')

    try:
        check_tweets(tweets)
    except TweetError as detail:
        app.logger.error(detail)
        return detail

    return "success"


def get_request_token():
    if 'request_token' in session:
        request_token = session['request_token']
    else:
        request_token = {'oauth_token': request.values.get('oauth_token'),
                         'oauth_verifier': request.values.get('oauth_verifier')}
        if ((request_token['oauth_token'] is not None) and
                (request_token['oauth_verifier'] is not None)):
            session['request_token'] = request_token
    return request_token


def get_access_token(request_token):
    if 'access_token' in session:
        access_token = session['access_token']
    else:
        try:
            access_token = tweet.get_access_token(request_token)
        except tweet.RequestDenied as detail:
            app.logger.error(detail)
            clean_session()
            flash(detail)
            return redirect('/logout')
        if ((access_token['oauth_token'] is not None) and
                (access_token['oauth_token_secret'] is not None)):
            session['access_token'] = access_token
    return access_token


def check_token():
    result = False
    if 'access_token' in session:
        result = True
    elif 'request_token' in session:
        result = True
    else:
        request_token = get_request_token()
        if ((request_token['oauth_token'] is not None) and
                (request_token['oauth_verifier'] is not None)):
            result = True
        else:
            result = False
    return result


def check_tweets(tweets):
    if isinstance(tweets, dict):
        if 'error' in tweets.keys():
            raise TweetError(tweets['error'])
        elif 'errors' in tweets.keys():
            raise TweetError(tweets['errors'][0]['message'])
    if len(tweets) == 0:
        raise TweetError("Tweet Not Found")
    return


def render_tweets(req, tweets):
    if req['twtype'] in ["lists"]:
        return render_template('lists.html', lists=tweets)
    elif req['twtype'] in ["friends"]:
        return render_template('lists.html', lists=tweets['users'])
    elif req['twtype'] in ["search"]:
        if 'statuses' in tweets.keys():
            tweets = tweets['statuses']
        return render_template('tweets.html', **locals())
    else:
        return render_template('tweets.html', **locals())


def clean_session():
    for s in ['request_token', 'access_token']:
        session.pop(s, None)


if __name__ == "__main__":
    app.debug = True
    app.run(threaded=True)
