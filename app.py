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
    elif tweet.check_token():
        return
    else:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)
        return redirect('/login')


@app.route('/login', methods=['GET'])
def login():
    redirect_url = tweet.get_redirect_url()
    app.logger.debug("redirect url: {}".format(redirect_url))
    return redirect(redirect_url)


@app.route('/logout', methods=['GET'])
def logout():
    print "INFO: logout"
    tweet.clean_session()
    return redirect('/login')


@app.route('/', methods=['GET'])
def index():
    try:
        access_token = tweet.get_access_token();
    except tweet.RequestDenied as detail:
        print "ERROR:", detail
        flash(detail)
        return redirect('/logout')
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

    tweets = get_tweets(request.json['twtype'], request.json['params'])
    if tweets is None:
        return redirect('/logout')

    rtn = check_tweets(tweets)
    if rtn is not None:
        return render_template('error.html', message=rtn)

    return render_tweets(request.json, tweets)


@app.route('/_post_tweets', methods=['POST'])
def _post_tweets():
    app.logger.debug("_post_tweets request: {}".format(request.json))

    tweets = get_tweets(request.json['twtype'], request.json['params'])
    if tweets is None:
        return redirect('/logout')

    rtn = check_tweets(tweets)
    if rtn is not None:
        return rtn
    else:
        return "success"


def get_tweets(twtype, params):
    t = tweet.Tweet()
    try:
        tweets = t.get_tweets(twtype, params)
    except tweet.RequestDenied as detail:
        print "ERROR:", detail
        return None
    return tweets


def check_tweets(tweets):
    if isinstance(tweets, dict):
        if 'error' in tweets.keys():
            return tweets['error']
        elif 'errors' in tweets.keys():
            return tweets['errors'][0]['message']
    if len(tweets) == 0:
        return "Tweet Not Found"
    return None


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
