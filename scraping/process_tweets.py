
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

    pattern = r"http\S+|\S+\.com\S+" # hyperlinks
    pattern += r"|pic\.\S+" # photos
    pattern += r"|@[a-zA-Z0-9_]+" # usertags
    pattern += r"|#[a-zA-Z0-9_]+" # hashtags

    s = re.sub(pattern, '', s)
    s = re.sub(r' +', ' ', re.sub(r'\r+|\t+|\n+', ' ', s)).strip()

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


def is_short(s, length_threshold = 10):
    """
    Checks whether a Tweet is short, by checking if it has at least 
    `length_threshold` words.

    Args:
        s (str): text
        length_threshold (int): word count threshold for input to be considered 
            short. Defaults to 10
    
    Returns:
        bool: True if text is short, False otherwise
    """

    n_words = len(s.split())
    return True if n_words < length_threshold else False


def clean_tweet_table(raw_data, length_threshold = 10, likes_threshold = 20):
    """
    Cleans a collection of Tweets, and returns the subset that are not replies 
    and meet the length and minimum like count criteria.

    Args:
        raw_data (pandas.DataFrame): table containing Tweets collected using `twint`
        length_threshold (int): word count threshold for Tweets to be included in 
            final dataset. Defaults to 10
        likes_threshold (int): likes count threshold for Tweets to be included in 
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
        functools.partial(is_short, length_threshold = length_threshold),
        raw_data.tweet_cleaned
    ))

    new_data = raw_data[(raw_data.is_short == False) & 
                        (raw_data.is_reply == False) & 
                        (raw_data.likes_count >= likes_threshold)].drop_duplicates(
                            subset = ['tweet_cleaned']
                        )
    
    return new_data


if __name__ == '__main__':

    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description = 'Clean up Tweet data'
    )

    parser.add_argument(
        '--raw_data_dir',
        type = Path,
        help = 'Directory for saving raw scraped text',
        default = Path(__file__).absolute().parent / 'data' / 'raw'
    )

    parser.add_argument(
        '--processed_data_dir',
        type = Path,
        help = 'Directory for saving processed scraped text',
        default = Path(__file__).absolute().parent / 'data' / 'processed'
    )

    parser.add_argument(
        '---output_data_dir',
        type = Path,
        help = 'Directory for saving combined cleaned data file',
        default = Path(__file__).absolute().parent / 'data' / 'final'
    )

    args = parser.parse_args()


    # Create folders for saving files
    if not args.processed_data_dir.exists():
        args.processed_data_dir.mkdir()

    if not args.output_data_dir.exists():
        args.output_data_dir.mkdir()


    # Iterate through raw data files for processing
    raw_files = args.raw_data_dir.glob('twitter_*.csv')
 
    tweets = pd.DataFrame()

    for raw_file in raw_files:

        raw_data = pd.read_csv(
            raw_file,
            converters = {"reply_to": literal_eval}
        )

        clean_data = clean_tweet_table(raw_data)

        fp_processed = args.processed_data_dir / f'{raw_file.stem}_cleaned.csv'
        clean_data.to_csv(fp_processed, index = False)

        tweets = tweets.append(
            clean_data, 
            ignore_index = True
        )

    tweets = tweets.drop_duplicates(subset = ['tweet_cleaned'])


    # Save final result as one file
    fp_output = args.output_data_dir / 'tweet_data.txt'
    with open(fp_output, 'w') as f:
        f.write('\n'.join(tweets.tweet_cleaned))

