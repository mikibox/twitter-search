from TwitterSearch import *
import configparser
import json
import os
import logging
import argparse

logger = logging.getLogger(__name__)
h = logging.StreamHandler()
h.setFormatter(logging.Formatter('%(asctime)s %(levelname)8s %(name)s | %(message)s'))
logger.addHandler(h)
logger.setLevel(logging.DEBUG)


config = configparser.ConfigParser()
config.read('config.ini')

DICT_NAME = None
CLEAN_USERS_LIST = None


def set_dict_name(name):
    global DICT_NAME
    DICT_NAME = name


def set_clean_users(users_list):
    global CLEAN_USERS_LIST
    CLEAN_USERS_LIST = users_list


def authenticate_twitter_search():
    ts = TwitterSearch(
        consumer_key=config['twitter']['consumer_key'],
        consumer_secret=config['twitter']['consumer_secret'],
        access_token=config['twitter']['access_token'],
        access_token_secret=config['twitter']['access_token_secret']
    )
    return ts


def read_file(path):
    with open(path, 'rU') as infile:
        lines = [line.strip() for line in infile]
    return lines


def create_custom_searches(words):
    tso_lang = TwitterSearchOrder()  # create a TwitterSearchOrder object
    tso_lang.set_keywords(words, or_operator=True)  # let's define all words we would like to have a look for
    tso_lang.set_language('es')  # we want to see German tweets only
    tso_lang.set_include_entities(False)  # and don't give us all those entity information

    tso_loc = TwitterSearchOrder()
    tso_loc.set_keywords(words, or_operator=True)
    tso_loc.set_geocode(float(config['location']['lat']),
                        float(config['location']['long']),
                        int(config['location']['dist']),
                        imperial_metric=False)
    tso_loc.set_include_entities(False)

    tso_list = {
        'lang': tso_lang,
        'loc': tso_loc
    }

    return tso_list


def clean_users(tso_list, users_list):
    for tso in tso_list:

        output = config['paths']['output'] + '{}_{}.json'.format(DICT_NAME, tso)

        # tweets_dict = {}
        with open(output, 'rU') as json_file:
            tweets_dict = json.load(json_file)

        # First clean up the twits
        new_tweets_dict = dict()
        count = 0
        for tweet in tweets_dict:
            if tweets_dict[tweet]['user']['id_str'] not in CLEAN_USERS_LIST:
                new_tweets_dict[tweet] = tweets_dict[tweet]
            else:
                count += 1

        with open(output, 'w') as outfile:
            json.dump(new_tweets_dict, outfile, indent=4)
        # print("cleaned {} tweets from {}".format(count, output))


def search_new_tweets(ts, tso_list):
    for tso in tso_list:
        output = config['paths']['output'] + '{}_{}.json'.format(DICT_NAME, tso)
        tweets_dict = {}
        count = 0

        if os.path.exists(output):
            with open(output) as json_file:
                tweets_dict = json.load(json_file)

        for tweet in ts.search_tweets_iterable(tso_list[tso]):
            tweet_existing = tweet['id_str'] not in tweets_dict.keys()
            tweet_popular = 'retweeted_status' not in tweet.keys()
            tweet_user_clean = tweet['user']['id_str'] not in CLEAN_USERS_LIST
            if tweet_existing and tweet_popular and tweet_user_clean:
                count += 1
                # print('@%s tweeted: %s' % (tweet['user']['screen_name'], tweet['text']))
                tweets_dict[tweet['id']] = tweet

        print("writing {} new twits".format(count))
        with open(output, 'w') as outfile:
            json.dump(tweets_dict, outfile, indent=4)

    # print(tweets_dict.keys())
    print("finished running twitter-search")


def main():
    parser = argparse.ArgumentParser(description='Twitter special search for a wordlist and a location')
    parser.add_argument('dictionary', metavar='dictionary', type=str, help='dictionary file to read')
    args = parser.parse_args()  # ['input.json', 'output.json'])

    set_dict_name(args.dictionary)
    clean_users_list = read_file('wordlist_clean_users')
    set_clean_users(clean_users_list)

    words = read_file(config['paths']['input'] + 'wordlist_{}'.format(args.dictionary))

    ts = authenticate_twitter_search()
    tso_list = create_custom_searches(words)
    search_new_tweets(ts, tso_list)
    clean_users(tso_list, clean_users_list)


if __name__ == '__main__':
    main()
