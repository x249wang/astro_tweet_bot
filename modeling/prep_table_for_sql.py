
if __name__ == "__main__":

    import argparse
    import pandas as pd
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description = 'Create table containing final list of Tweets')

    parser.add_argument(
        '--input_file_path',
        type = Path,
        default = Path(__file__).absolute().parent / 'output' / 'bot_tweets_cleaned.txt',
        help = 'Filepath to where text is stored'
    )

    parser.add_argument(
        '--output_file_path',
        type = Path,
        default = Path(__file__).absolute().parent / 'output' / 'tweets.csv',
        help = 'Filepath to where final table of tweets is stored'
    )

    args = parser.parse_args()


    # Load list of Tweets and convert to csv table
    with open(args.input_file_path, 'r') as f:
        tweets = [line.strip() for line in f.readlines()]

    tweets_table = pd.DataFrame({
        'id': range(len(tweets)),
        'tweet': tweets,
        'tweet_timestamp': '', 
        'tweet_url': ''
    })

    tweets_table.to_csv(args.output_file_path, header = False, index = False)

