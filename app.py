#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import logging
import json
from datetime import timedelta
from flask import Flask, session, request, redirect, render_template
from flask_assets import Environment, Bundle
from lib import tweet

CONFIG_FILE = "etc/tweet.json"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('scss/style.scss', filters='pyscss', output='css/style.css')
assets.register('style_scss', scss)

@app.before_request
def before_request():
    print "INFO: before_request"
    if request.path == '/login':
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
    print "INFO: login"
    t = tweet.Tweet(CONFIG_FILE)
    redirect_url = t.get_redirect_url()
    return redirect(redirect_url)


@app.route('/logout', methods=['GET'])
def logout():
    print "INFO: logout"
    tweet.clean_session()
    return redirect('/login')


@app.route("/")
def index():
    print "INFO: index"
    t = tweet.Tweet(CONFIG_FILE)
    t.set_access_token()
    tweets = t.get_tweets("timeline", {'count': 100})
    with open("timeline.json", 'w') as f:
        json.dump(tweets, f)

    if isinstance(tweets, dict):
        if 'errors' in tweets.keys():
            print "ERROR: ", tweets
            return redirect('/logout')

    for t in tweets[:]:
        if 'extended_entities' not in t.keys():
            tweets.remove(t)
    return render_template('index.html', tweets=tweets)


if __name__ == "__main__":
    app.debug = True
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.run(threaded=True)
