
import os
import time
import twint

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
    
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description = 'Scrape Tweets from select Twitter accounts'
    )

    parser.add_argument(
        '--data_dir',
        type = Path,
        help = 'Directory for saving Tweet data',
        default = Path(__file__).absolute().parent / 'data' / 'raw'
    )

    parser.add_argument(
        '--accounts_list',
        type = Path,
        help = 'File path to text file containing list of Twitter accounts to scrape',
        default = Path(__file__).absolute().parent / 'twitter_accounts.txt'
    )

    parser.add_argument(
        '--config_params',
        metavar = 'KEY=VALUE',
        nargs = '*',
        help = 'Configuration parameters for Twint search (optional) as key value pairs (format: --config_params KEY=VALUE)'
    )

    args = parser.parse_args()


    # Create folder for saving files
    if not args.data_dir.exists():
        args.data_dir.mkdir(parents = True)


    # Read in list of Twitter accounts to scrape
    with open(args.accounts_list, 'r') as fp:
        accounts = [line.strip() for line in fp.readlines()]

    # Config parameters for Twint search
    # Defaults to recent Tweets (2018 and later), saved to csv
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

    if args.config_params:
        for param in args.config_params:
            key, value = param.split('=')
            params[key] = value


    for account in accounts:
        
        fp = args.data_dir / f'twitter_{account}.csv'
        params['Output'] = str(fp)
        params['Username'] = account
        
        ts = TweetSearch(**params)
        ts.run()

        time.sleep(60 * 2)

