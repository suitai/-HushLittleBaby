#!/usr/bin/env python
# -*- coding:utf-8 -*-


import sys
import getopt
import cuitweet
import download

### Functions
def check_optlist(optlist):
    option = {}
    option_keys = {
            "-c": "count",
            "-s": "since_id",
            "-m": "max_id",
            "-o": "out_dir",
            "-k": "key_file"
            }
    for opt, arg in optlist:
        if opt in option_keys.keys():
            option[option_keys[opt]] = arg
        else:
            assert False, "unhandled option"
    return option

def tweet_get_favorite_media(args, optlist):
    opt = check_optlist(optlist)
    out_dir = opt['out_dir'] if opt.has_key('out_dir') else "./"
    key_file = opt['key_file'] if opt.has_key('key_file') else ("tweet_keys.yaml")

    Tw = cuitweet.Tweet(key_file)
    tweets = Tw.get_favorite(opt)
    num = len(tweets)
    first_id = tweets[0][u'id']
    last_id = tweets[-1][u'id']
    for tw in tweets:
        print "<https://twitter.com/%s/status/%d>" % (tw[u'user'][u'screen_name'], tw[u'id'])
        if "media" in tw[u'entities']:
            for media in tw[u'entities'][u'media']:
                try:
                    download.download(media[u'media_url'], out_dir)
                except download.DownloadError as detail:
                    print detail
        print ""
    return num, first_id, last_id

def main():
    raw_args = sys.argv
    try:
        optlist, args = getopt.getopt(raw_args[1:], 'c:k:m:o:s:')
    except getopt.GetoptError as detail:
        sys.exit("GetoptError: %s" % detail)
    args.insert(0, raw_args[0])
    num, first_id, last_id = tweet_get_favorite_media(args, optlist)


### Execute
if __name__ == "__main__":
    main()
