if __name__ == "__main__":

    import pandas as pd
    from pathlib import Path

    # Load list of Tweets and convert to csv table
    input_file_path = Path("./output/bot_tweets_cleaned.txt")

    with open(input_file_path, "r") as f:
        tweets = [line.strip() for line in f.readlines()]

    tweets_table = pd.DataFrame(
        {
            "id": range(len(tweets)),
            "tweet": tweets,
            "tweet_timestamp": "",
            "tweet_url": "",
        }
    )

    output_file_path = Path("./output/tweets.csv")
    tweets_table.to_csv(output_file_path, header=False, index=False)
