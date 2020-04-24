
import os
import re
import functools
import numpy as np
import pandas as pd
from ast import literal_eval

def clean_text(s):
    """
    Cleans text to remove links, usertags, hashtags, emojis, extra whitespaces.
    Note that numbers, punctuation marks and casing are kept. 
    
    Args:
        s (str): raw text

    Returns:
        str: cleaned text
    """

    pattern = "http\S+|\S+\\.com\S+" # hyperlinks
    pattern += "|pic\\.\S+" # photos
    pattern += "|@[a-zA-Z0-9_]+" # usertags
    pattern += "|#[a-zA-Z0-9_]+" # hashtags

    s = re.sub(pattern, '', s)

    s = re.sub(' +', ' ', re.sub('\r+|\t+|\n+', ' ', s)).strip()

    return s.encode('ascii', 'ignore').decode('ascii')


def is_reply(s, user, reply_to):
    """
    Checks whether a Tweet is a reply to someone else's Tweet, since 
    this is not provided by `twint` output. 

    If a user is part of the reply_to field, and was not mentioned in the 
    text itself (i.e. a mention), then the Tweet is considered a reply.

    Args:
        s (str): Tweet text
        user (str): username of Tweet owner/writer
        reply_to (list): list of users in the reply_to field returned by `twint`
    
    Returns:
        bool: True if the Tweet is a reply, False otherwise
    """

    users = [u['username'] for u in reply_to]

    users_replied = [u for u in users 
                     if (u not in s) and (u.lower() != user.lower())]

    return True if users_replied else False


def is_short(s, len_thres = 10):
    """
    Checks whether a Tweet is short, by checking if it has at least 
    `len_thres` words.

    Args:
        s (str): text
        len_thres (int): word count threshold for input to be considered short.
            Defaults to 10
    
    Returns:
        bool: True if text is short, False otherwise
    """

    n_words = len(s.split())
    return True if n_words < len_thres else False


def clean_tweet_df(raw_data, len_thres = 10, likes_thres = 20):
    """
    Cleans a collection of Tweets, and returns the subset that are not replies 
    and meet the length and minimum like count criteria.

    Args:
        raw_data (pandas.DataFrame): table containing Tweets collected using `twint`
        len_thres (int): word count threshold for Tweets to be included in 
            final dataset. Defaults to 10
        likes_thres (int): likes count threshold for Tweets to be included in 
            final dataset. Defaults to 20

    Returns:
        pandas.DataFrame of cleaned Tweets that met the filtering criteria
    """

    raw_data['tweet_cleaned'] = list(map(
        clean_text, 
        raw_data.tweet
    ))

    raw_data['is_reply'] = list(map(
        is_reply, 
        raw_data.tweet,
        raw_data.username, 
        raw_data.reply_to
    ))

    raw_data['is_short'] = list(map(
        functools.partial(is_short, len_thres = len_thres),
        raw_data.tweet_cleaned
    ))

    new_data = raw_data[(raw_data.is_short == False) & 
                        (raw_data.is_reply == False) & 
                        (raw_data.likes_count >= likes_thres)].drop_duplicates(
                            subset = ['tweet_cleaned']
                        )
    
    return new_data


if __name__ == '__main__':

    if not os.path.exists('data/cleaned'):
        os.mkdir('data/cleaned')

    if not os.path.exists('data/final'):
        os.mkdir('data/final')


    with open('data/astro_twitter_accounts.txt', 'r') as f:
        accounts = f.readlines()
        accounts = [account.strip() for account in accounts]
 
    # Cleans raw data and combine into a single file
    all_tweets = pd.DataFrame()

    for account in accounts:

        raw_data_i = pd.read_csv(
            f'data/raw/{account}.csv', 
            converters = {
                "reply_to": literal_eval
            }
        )

        clean_data_i = clean_tweet_df(raw_data_i)
        clean_data_i.to_csv(f'data/cleaned/{account}_cleaned.csv')

        all_tweets = all_tweets.append(
            clean_data_i, 
            ignore_index = True
        )


    all_tweets = all_tweets.drop_duplicates(subset = ['tweet_cleaned'])

    # Format expected for model fine-tuning script
    all_tweets.tweet_cleaned.to_csv(
        'data/final/tweet_data.txt', 
        index = False, 
        header = False
    )

