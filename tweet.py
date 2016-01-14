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
        self.tweets = None

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
            if responce.status_code == 200:
                return json.loads(responce.text)
            else:
                raise TweetError("Error: %d %s" % (responce.status_code, httplib.responses[responce.status_code]))
        else:
            assert False, "not create oath session yet"

    def get_timeline(self, count=20):
        params = {
                "count": count,
                "include_entities": True
                }
        self.tweets = self.get_from_oath("timeline", params = params)

    def get_favorite(self, count=20):
        params = {
                "count": count,
                "include_entities": True
                }
        self.tweets = self.get_from_oath("favorite", params = params)

    def search_tweets(self, search_term, count=20):
        params = {
                "q": search_term,
                "result_type": "recent",
                "count": count,
                "include_entities": True
                }
        self.tweets = self.get_from_oath("search", params = params)['statuses']

    def get_list(self, list_id, slug, count=20):
        params = {
                "list_id": list_id,
                "slug": slug,
                "count": count,
                "include_entities": True
                }
        self.tweets = self.get_from_oath("list", params = params)

    def get_list_by_name(self, list_name, count=20):
        params = {}
        lists = self.get_from_oath("lists", params = params)
        for tweet_list in lists:
            if tweet_list[u'name'] == list_name:
                self.get_list(tweet_list[u'id'], tweet_list[u'slug'], count=count)
                break
        else:
            raise TweetError("Cannot find list")

    def print_tweets(self):
        for tweet in self.tweets:
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
    option = {
            "count": None
            }
    for opt, arg in optlist:
        if opt == "-n":
            option['count'] = int(arg)
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
    tweet.get_timeline(count = opt['count'])
    tweet.print_tweets()

def tweet_show_favorite(args, optlist):
    opt = check_optlist(optlist)
    tweet = tweet_init()
    tweet.get_favorite(count = opt['count'])
    tweet.print_tweets()

def tweet_search_tweets(args, optlist):
    if len(args) > 2:
        opt = check_optlist(optlist)
        tweet = tweet_init()
        tweet.search_tweets(args[2], count = opt['count'])
        tweet.print_tweets()
    else:
        print "Usage: %s %s \"search term\"" % (args[0], args[1])

def tweet_show_list(args, optlist):
    if len(args) > 2:
        opt = check_optlist(optlist)
        tweet = tweet_init()
        tweet.get_list_by_name(args[2], count = opt['count'])
        tweet.print_tweets()
    else:
        print "Usage: %s %s \"list name\"" % (args[0], args[1])

functions = {
        "timeline": tweet_show_timeline,
        "favorite": tweet_show_favorite,
        "list": tweet_show_list,
        "search": tweet_search_tweets,
        }


### Execute
if __name__ == "__main__":
    raw_args = sys.argv
    try:
        optlist, args = getopt.getopt(raw_args[1:], 'n:')
    except getopt.GetoptError as detail:
        sys.exit("GetoptError: %s" % detail)
    args.insert(0, raw_args[0])
    if (len(args) > 1) and (args[1] in functions.keys()):
       functions[args[1]](args, optlist)
    else:
        print "Usage: [option] %s %s [args]" % (args[0], functions.keys())
