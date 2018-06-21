from TwitterSearch import *
import configparser
import json
import os

try:

    try:
        with open('wordlist', 'rU') as infile:
            wordSet = [line.strip() for line in infile]
    except IOError:
        raise IOError

    tso = TwitterSearchOrder()  # create a TwitterSearchOrder object
    tso.set_keywords(wordSet, or_operator=True)  # let's define all words we would like to have a look for
    tso.set_language('es')  # we want to see German tweets only
    tso.set_include_entities(False)  # and don't give us all those entity information

    # it's about time to create a TwitterSearch object with our secret tokens
    config = configparser.ConfigParser()
    config.read('config.ini')
    ts = TwitterSearch(
        consumer_key=config['twitter']['consumer_key'],
        consumer_secret=config['twitter']['consumer_secret'],
        access_token=config['twitter']['access_token'],
        access_token_secret=config['twitter']['access_token_secret']
    )

    # this is where the fun actually starts :)
    tweets_dict = {}

    # read the previous tweets
    if os.path.exists('data.json'):
        with open('data.json') as json_file:
            tweets_dict = json.load(json_file)

    print(tweets_dict)

    for tweet in ts.search_tweets_iterable(tso):
        if tweet['id_str'] not in tweets_dict.keys() and tweet['retweet_count'] >= 20 and 'retweeted_status' not in tweet.keys():
            print('@%s tweeted: %s' % (tweet['user']['screen_name'], tweet['text']))
            tweets_dict[tweet['id']] = tweet

    with open('data.json', 'w') as outfile:
        json.dump(tweets_dict, outfile, indent=4)

    print(tweets_dict.keys())

except TwitterSearchException as e:  # take care of all those ugly errors if there are some
    print(e)
