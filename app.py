#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
from datetime import timedelta
from flask import Flask, session, request, redirect, render_template, flash, jsonify
from flask_assets import Environment, Bundle
from lib import tweet

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['JSON_AS_ASCII'] = False

assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('scss/style.scss', filters='pyscss', output='css/style.css')
assets.register('style_scss', scss)

logout_page = '/logout'
login_page = '/login'


class TweetError(Exception):
    pass


class TokenError(Exception):
    pass


@app.before_request
def before_request():
    if request.path == '/login':
        return
    elif request.path == logout_page:
        return
    elif request.path[-4:] == ".css":
        return
    elif request.path[-3:] == ".js":
        return
    elif check_token():
        return
    else:
        return redirect('/login')


@app.route('/login', methods=['GET'])
def login():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=10)

    try:
        redirect_url = tweet.get_redirect_url()
    except tweet.RequestDenied as detail:
        app.logger.error(detail)
        clean_session()
        raise
    return redirect(redirect_url)


@app.route(logout_page, methods=['GET'])
def logout():
    clean_session()
    return redirect(login_page)


@app.route('/', methods=['GET'])
def index():
    try:
        request_token = get_request_token()
        access_token = get_access_token(request_token)

    except TokenError as detail:
        app.logger.error(detail)
        return redirect(login_page)

    except tweet.RequestDenied as detail:
        app.logger.error(detail)
        return redirect(logout_page)

    except TokenError:
        return redirect(logout_page)

    return render_template('index.html', screen_name=access_token['screen_name'])


@app.route('/_get_ipaddr')
def get_ipaddr():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    app.logger.info("ipaddr: {}".format(ip))
    return jsonify({'ip': ip})


@app.route('/_get_tweets_head')
def _get_tweets_head():
    return render_template('tweets-head.html')


@app.route('/_get_tweet_template')
def _get_tweet_template():
    return render_template('tweet.html')


@app.route('/_get_tweets_js', methods=['POST'])
def _get_tweets_js():
    app.logger.debug("_get_tweets_js request: {}".format(request.json))
    try:
        request_token = get_request_token()
        access_token = get_access_token(request_token)
        tweets = tweet.get_tweets(access_token, request.json['twtype'], request.json['params'])

    except TokenError as detail:
        app.logger.error(detail)
        return redirect(login_page)

    except tweet.RequestDenied as detail:
        app.logger.error(detail)
        return jsonify({'error': str(detail)})

    try:
        check_tweets(tweets)
    except TweetError as detail:
        app.logger.error(detail)
        return jsonify({'error': str(detail)})

    send_data = filter_data(request.json['twtype'], tweets)

    return jsonify(send_data)


@app.route('/_get_oath2_tweets_js', methods=['POST'])
def _get_oath2_tweets():
    app.logger.debug("_get_oath2_tweets request: {}".format(request.json))
    try:
        access_token = get_oath2_access_token()
        tweets = tweet.get_oath2_tweets(access_token, request.json['twtype'], request.json['params'])

    except tweet.RequestDenied as detail:
        app.logger.error(detail)
        app.logger.error(detail)
        return jsonify({'error': str(detail)})

    try:
        check_tweets(tweets)
    except TweetError as detail:
        app.logger.error(detail)
        return jsonify({'error': str(detail)})

    send_data = filter_data(request.json['twtype'], tweets)

    return jsonify(send_data)


@app.route('/_get_tweets', methods=['POST'])
def _get_tweets():
    app.logger.debug("_get_tweets request: {}".format(request.json))
    try:
        request_token = get_request_token()
        access_token = get_access_token(request_token)
        tweets = tweet.get_tweets(access_token, request.json['twtype'], request.json['params'])

    except TokenError as detail:
        app.logger.error(detail)
        return redirect(login_page)

    except tweet.RequestDenied as detail:
        app.logger.error(detail)
        return redirect(logout_page)

    try:
        check_tweets(tweets)
    except TweetError as detail:
        app.logger.error(detail)
        return render_template('error.html', message=detail)

    return render_tweets(request.json, tweets)


@app.route('/_post_tweets', methods=['POST'])
def _post_tweets():
    app.logger.debug("_post_tweets request: {}".format(request.json))
    try:
        request_token = get_request_token()
        access_token = get_access_token(request_token)
        tweets = tweet.get_tweets(access_token, request.json['twtype'], request.json['params'])

    except TokenError as detail:
        app.logger.error(detail)
        return redirect(login_page)

    except tweet.RequestDenied as detail:
        app.logger.error(detail)
        return redirect(logout_page)

    try:
        check_tweets(tweets)
    except TweetError as detail:
        app.logger.error(detail)
        return detail.args

    return "success"


def get_oath2_access_token():
    if 'oath2_access_token' in session:
        access_token = session['oath2_access_token']

    else:
        try:
            access_token = tweet.get_oath2_access_token()
            session['oath2_access_token'] = access_token

        except tweet.RequestDenied:
            raise

    return access_token


def get_request_token():
    if 'request_token' in session:
        request_token = session['request_token']
    else:
        oauth_token = request.args.get('oauth_token')
        oauth_verifier = request.args.get('oauth_verifier')
        if oauth_token is None or oauth_verifier is None:
            raise TokenError('cannot get request token')

        else:
            request_token = {'oauth_token': oauth_token,
                             'oauth_verifier': oauth_verifier}
            session['request_token'] = request_token

    return request_token


def get_access_token(request_token):
    if 'access_token' in session:
        access_token = session['access_token']
    else:
        try:
            access_token = tweet.get_access_token(request_token)
            app.logger.info("screen_name: {}".format(access_token['screen_name']))
            session['access_token'] = access_token

        except tweet.RequestDenied:
            raise

    return access_token


def check_token():
    if 'access_token' in session:
        return True

    if 'request_token' in session:
        return True

    try:
        get_request_token()
    except TokenError:
        return False
    else:
        return True


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


def filter_data(twtype, tweets):
    send_data = None

    if twtype in ["lists"]:
        send_data = filter_lists(tweets)
    elif twtype in ["friends"]:
        send_data = filter_lists(tweets['users'])
    elif twtype in ["search"]:
        send_data = filter_tweets(tweets)
    elif twtype in ["geosearch"]:
        send_data = tweets
    else:
        send_data = filter_tweets(tweets)

    return send_data


def filter_tweets(tweets):
    send_tweets = []

    if isinstance(tweets, dict):
        if 'statuses' in tweets.keys():
            tweets = tweets['statuses']

    for tw in tweets:
        if 'media' not in tw['entities']:
            continue
        tweet_id = str(tw['id'])
        if 'retweeted_status' in tw.keys():
            tw = tw['retweeted_status']
        tweet_id_org = str(tw['id'])
        tmp_tw = {'id': tweet_id,
                  'id_org': tweet_id_org,
                  'media_url_https': tw['entities']['media'][0]['media_url_https'],
                  'user_id': tw['user']['id'],
                  'user_screen_name': tw['user']['screen_name'],
                  'user_name': tw['user']['name'],
                  'text': tw['text'],
                  'retweet_count': tw['retweet_count'],
                  'favorite_count': tw['favorite_count'],
                  'retweeted': tw['retweeted'],
                  'favorited': tw['favorited']}
        send_tweets.append(tmp_tw)
    return send_tweets


def filter_lists(tweets):
    send_lists = []
    for tw in tweets:
        tmp_tw = {'id': str(tw['id']),
                  'name': tw['name']}
        send_lists.append(tmp_tw)
    return send_lists


def clean_session():
    for s in ['request_token', 'access_token', 'oath2_access_token']:
        session.pop(s, None)


if __name__ == "__main__":
    app.debug = True
    app.run(threaded=True)
