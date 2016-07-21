#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import logging
import json
from datetime import timedelta
from flask import Flask, session, request, redirect, render_template
from lib import tweet


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


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
        tweet.clean_session()
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)
        return redirect('/login')


@app.route('/login', methods=['GET'])
def login():
    print "INFO: login"
    t = tweet.Tweet()
    redirect_url = t.get_redirect_url()
    return redirect(redirect_url)


@app.route("/")
def index():
    print "INFO: index"
    t = tweet.Tweet()
    t.set_access_token()
    tweets = t.get_tweets("timeline", {'count': 100})
    with open("timeline.json", 'w') as f:
        json.dump(tweets, f)
    for t in tweets[:]:
        if 'extended_entities' not in t.keys():
            tweets.remove(t)
    return render_template('index.html', tweets=tweets)


if __name__ == "__main__":
    app.debug = True
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.run(threaded=True)
