
import os
import time
import twint
from ast import literal_eval

# Used to enable concurrent actions within a Jupyter notebook
# Not needed if not using a notebook
# import nest_asyncio
# nest_asyncio.apply()

class TweetSearch(object):
    """
    Searches for Tweets by leveraging the `twint` package; essentially a wrapper.

    Args:
        **kwargs: configuration options for `twint` search. 
                  See https://github.com/twintproject/twint/wiki/Configuration
    """

    def __init__(self, **kwargs):

        self.c = twint.Config()

        for k in kwargs:
            setattr(self.c, k, kwargs[k])

    def run(self):
        """
        Executes search for Tweets.
        """
        twint.run.Search(self.c)


if __name__ == "__main__":
    
    if not os.path.exists('data/raw'):
        os.mkdir('data/raw')

    # Collects recent Tweets from a list of astrology accounts
    params = {
        'Lang': 'en',
        'Since': "2018-01-01 0:0:0",
        'Images': False,
        'Videos': False,
        'Media': False,
        'Filter_retweets': True,
        'Limit': 10000,
        'Store_csv': True,
        'Hide_output': True
    }

    with open('data/astro_twitter_accounts.txt', 'r') as f:
        accounts = f.readlines()
        accounts = [account.strip() for account in accounts]

    for account in accounts:
        
        params['Output'] = f'data/raw/{account}.csv'
        params['Username'] = account
        
        ts = TweetSearch(**params)
        ts.run()

        time.sleep(60 * 10)

