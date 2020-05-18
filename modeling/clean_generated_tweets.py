import random
from nltk.tokenize import sent_tokenize


def remove_incomplete_sentences(s):
    """
    Removes incomplete sentences from a block of text.

    Args:
        s (str): input block of text

    Return:
        str: text with incomplete sentences removed
    """

    sentences = sent_tokenize(s)

    if s[-1][-1] not in [".", "!", "?", ""] and len(sentences) > 1:
        sentences = sentences[:-1]

    return " ".join(sentences)


if __name__ == "__main__":

    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Clean generated Tweets")

    parser.add_argument(
        "--input_file_path",
        type=Path,
        default=Path(__file__).absolute().parent
        / "output"
        / "bot_tweets_raw.txt",
        help="Filepath to where raw text is stored",
    )

    parser.add_argument(
        "--output_file_path",
        type=Path,
        default=Path(__file__).absolute().parent
        / "output"
        / "bot_tweets_cleaned.txt",
        help="Filepath to where processed text should be stored",
    )

    parser.add_argument(
        "--max_char_length",
        type=int,
        default=280,
        help="Maximum character count for each line of text (i.e. Tweet). Max allowable is 280",
    )

    args = parser.parse_args()

    # Load raw texts
    with open(args.input_file_path, "r") as f:
        tweets = [line.strip() for line in f.readlines()]

    # Process text by removing incomplete sentences and
    # those over the character count limit
    tweets = [remove_incomplete_sentences(tweet) for tweet in tweets]

    max_char_length = min(args.max_char_length, 280)
    tweets = list(filter(lambda x: len(x) <= max_char_length, tweets))

    random.shuffle(tweets)

    # Save output
    with open(args.output_file_path, "w") as f:
        f.write("\n".join(tweets))
