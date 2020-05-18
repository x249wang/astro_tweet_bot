
import re

def keep_paragraph(paragraph, length_threshold = 10):
    """
    Applies exclusion criteria on a block of text by regex patterns and 
    word count length. 

    Args:
        para (str): text input
        len_thres (int): minimum word count length for text to be kept. 
            Defaults to 10
    
    Returns:
        bool: True if passed filtering criteria, False otherwise
    """

    if paragraph == '' or len(paragraph.split()) < length_threshold:
        return False
    
    pattern = r'^RELATED: '
    pattern += r'|follow (her|him|them) on (Instagram|Twitter|Snapchat|Tumblr)'
    pattern += r'|Refinery29|PureWow'
    pattern += r'|[sS]hop [tT]his|[bB]uy [tT]his'

    if re.search(pattern, paragraph):
        return False
        
    return True


def clean_text(s):
    """
    Cleans text to remove links, usertags,emojis, extra whitespaces.
    Note that numbers, punctuation marks and casing are kept. 
    
    Args:
        s (str): raw text

    Returns:
        str: cleaned text
    """

    pattern = r"http\S+|\S+\.com\S+" # hyperlinks
    pattern += r"|@[a-zA-Z0-9_]+" # usertags

    s = re.sub(pattern, '', s)
    s = re.sub(' +', ' ', re.sub('\r+|\t+|\n+', ' ', s)).strip()

    return s.encode('ascii', 'ignore').decode('ascii')


def clean_article_text(text_chunks):
    """
    Cleans and filters text chunks (e.g. remove text that are too short).

    Args:
        text_chunks (list of str): list of raw text chunks to be processed
    
    Returns:
        list of str: list of cleaned up text chunks that passed filtering criteria
    """

    cleaned_text = list(filter(
        keep_paragraph,
        [clean_text(t) for t in text_chunks]
    ))

    return cleaned_text


if __name__ == '__main__':

    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description = 'Clean articles text')

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
    raw_files = args.raw_data_dir.glob('articles_*.txt')

    articles = []

    for raw_file in raw_files:

        with open(raw_file, 'r', encoding = 'utf-8') as fp:
            raw_text = [line.strip() for line in fp.readlines()]

        cleaned_text = clean_article_text(raw_text)

        fp_processed = args.processed_data_dir / f'{raw_file.stem}_cleaned.txt'
        with open(fp_processed, 'a') as f:
            f.write('\n'.join(cleaned_text) + '\n')
        
        articles += cleaned_text


    # Save final result as one file
    fp_output = args.output_data_dir / 'article_data.txt'
    with open(fp_output, 'w') as f:
        f.write('\n'.join(articles))

