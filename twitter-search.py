from TwitterSearch import *
import configparser
import json
import os


try:

    try:
        with open('wordlist', 'rU') as infile:
            wordSet = [line.strip() for line in infile]

        with open('wordlist_clean_users', 'rU') as infile:
            users_ids = [line.strip() for line in infile]

        with open('data.json', 'rU') as json_file:
            tweets_dict = json.load(json_file)

    except IOError:
        raise IOError

    # First clean up the twits
    new_tweets_dict = dict()
    for tweet in tweets_dict:
        if tweets_dict[tweet]['user']['id_str'] not in users_ids:
            new_tweets_dict[tweet] = tweets_dict[tweet]

    with open('data.json', 'w') as outfile:
        json.dump(new_tweets_dict, outfile, indent=4)
    print("cleaned users success")

    print("searching for new twits")
    # Search for new twits
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

    print("capturing twits")

    for tweet in ts.search_tweets_iterable(tso):
        tweet_existing = tweet['id_str'] not in tweets_dict.keys()
        tweet_popular = tweet['retweet_count'] >= 2 and 'retweeted_status' not in tweet.keys()
        tweet_user_clean = tweet['user']['id_str'] not in users_ids
        if tweet_existing and tweet_popular and tweet_user_clean:
            print('@%s tweeted: %s' % (tweet['user']['screen_name'], tweet['text']))
            tweets_dict[tweet['id']] = tweet

    print("writing new twits")
    with open('data.json', 'w') as outfile:
        json.dump(tweets_dict, outfile, indent=4)

    # print(tweets_dict.keys())
    print("finished running twitter-search")

except TwitterSearchException as e:  # take care of all those ugly errors if there are some
    print(e)


