#!/usr/bin/env python
# -*- coding:utf-8 -*-

from requests_oauthlib import OAuth1Session
import json
import yaml
import sys
import httplib
import getopt
import pprint


class Tweet(object):
    def __init__(self):
        self.urls = {
                "search": "https://api.twitter.com/1.1/search/tweets.json",
                "timeline": "https://api.twitter.com/1.1/statuses/home_timeline.json",
                "favorite": "https://api.twitter.com/1.1/favorites/list.json",
                "lists": "https://api.twitter.com/1.1/lists/list.json",
                "list": "https://api.twitter.com/1.1/lists/statuses.json"
                }
        self.keys = None
        self.oath = None
        self.params = {}

    def add_params(self, params):
        for key, value in params.iteritems():
            self.params[key] = value

    def load_keys(self, filename="keys.yaml"):
        with open(filename, 'r') as stream:
            self.keys = yaml.load(stream)
        # TODO ファイルチェック

    def create_session(self):
        if self.keys != None:
            self.oath = OAuth1Session(
                    self.keys['consumer_key'],
                    self.keys['consumer_secret'],
                    self.keys['access_token'],
                    self.keys['access_token_secret']
                    )
        else:
            assert False, "not load keys yet"

    def get_from_oath(self, url, params):
        if self.oath != None:
            responce = self.oath.get(self.urls[url], params = params)
            if responce.status_code != 200:
                raise TweetError("%d %s" % (responce.status_code, httplib.responses[responce.status_code]))
        else:
            assert False, "not create oath session yet"
        return json.loads(responce.text)

    def get_timeline(self):
        self.params['include_entities'] = True
        return self.get_from_oath("timeline", params=self.params)

    def get_favorite(self):
        self.params['include_entities'] = True
        return self.get_from_oath("favorite", params=self.params)

    def search_tweets(self, search_term):
        self.params['q'] = search_term
        self.params['result_type'] = "recent"
        self.params['include_entities'] = True
        return self.get_from_oath("search", params=self.params)['statuses']

    def get_list(self, list_id):
        self.params['list_id'] = list_id
        self.params['include_entities'] = True
        return self.get_from_oath("list", params=self.params)

    def search_list(self, list_name):
        lists = self.get_from_oath("lists", params={})
        for tweet_list in lists:
            if tweet_list[u'name'] == list_name:
                break
        else:
            raise TweetError("Cannot find list \"%s\"" % list_name)
        return tweet_list[u'id']

    def get_list_by_name(self, list_name):
        list_id = self.search_list(list_name)
        return self.get_list(list_id)

    def print_tweets(self, tweets):
        for tweet in tweets:
            user = tweet[u'user']
            message =[]
            message.append("<https://twitter.com/%s/status/%d>" % (user[u'screen_name'], tweet[u'id']))
            message.append("[%d] %s" % (tweet[u'id'], tweet[u'created_at']))
            message.append("[%d] %s @%s" % (user[u'id'], user[u'name'], user[u'screen_name']))
            message.append("retweet: %d, favourite: %d" % (tweet[u'retweet_count'], tweet[u'favorite_count']))
            message.append(tweet[u'text'])
            print ("\n".join(message)).encode('utf-8')
            if "media" in tweet[u'entities']:
                for media in tweet[u'entities'][u'media']:
                    print ("<%s>" % media[u'media_url']).encode('utf-8')
            print ""


class TweetError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


### Functions
def check_optlist(optlist):
    option = {}
    option_keys = {
            "-n": "count",
            "-s": "since_id"
            }
    for opt, arg in optlist:
        if opt in option_keys.keys():
            option[option_keys[opt]] = int(arg)
        else:
            assert False, "unhandled option"
    return option

def tweet_init():
    tweet = Tweet()
    tweet.load_keys()
    tweet.create_session()
    return tweet

def tweet_show_timeline(args, optlist):
    opt = check_optlist(optlist)
    tweet = tweet_init()
    tweet.add_params(opt)
    tweets = tweet.get_timeline()
    tweet.print_tweets(tweets)

def tweet_show_favorite(args, optlist):
    opt = check_optlist(optlist)
    tweet = tweet_init()
    tweet.add_params(opt)
    tweets = tweet.get_favorite()
    tweet.print_tweets(tweets)

def tweet_search_tweets(args, optlist):
    if len(args) > 2:
        opt = check_optlist(optlist)
        tweet = tweet_init()
        tweet.add_params(opt)
        tweets = tweet.search_tweets(args[2])
        tweet.print_tweets(tweets)
    else:
        print "Usage: %s %s \"search term\"" % (args[0], args[1])

def tweet_show_list(args, optlist):
    if len(args) > 2:
        opt = check_optlist(optlist)
        tweet = tweet_init()
        tweet.add_params(opt)
        tweets = tweet.get_list_by_name(args[2])
        tweet.print_tweets(tweets)
    else:
        print "Usage: %s %s \"list name\"" % (args[0], args[1])


### Execute
if __name__ == "__main__":
    functions = {
        "timeline": tweet_show_timeline,
        "favorite": tweet_show_favorite,
        "list": tweet_show_list,
        "search": tweet_search_tweets,
        }
    raw_args = sys.argv
    try:
        optlist, args = getopt.getopt(raw_args[1:], 'n:s:')
    except getopt.GetoptError as detail:
        sys.exit("GetoptError: %s" % detail)
    args.insert(0, raw_args[0])
    if (len(args) > 1) and (args[1] in functions.keys()):
        try:
            functions[args[1]](args, optlist)
        except TweetError as detail:
            sys.exit("Error: %s" % detail)
    else:
        print "Usage: %s [option] %s [args]" % (args[0], functions.keys())
