import re
import time
from urllib import request
from urllib.parse import urljoin
from urllib.error import HTTPError
from bs4 import BeautifulSoup


def get_article_links(base_url, tags, links_to_excl=" ", links_to_incl=""):
    """
    Collects relevant hyperlinks from a given webpage.

    Args:
        base_url (str): webpage to look for links
        tags (list of tuples): attributes by which to look for relevant links.
            For example, `(div, id, post-123)` means looking for `div` with the
            id post-123.
        links_to_excl (str): regular expression pattern of hyperlinks to exclude.
            Defaults to no criteria (i.e. keep all links)
        links_to_incl (str): regular expression pattern of hyperlinks to keep.
            Defaults to no criteria (i.e. keep all links)

    Returns:
        list of str: list of links
    """

    r = request.urlopen(base_url).read()
    soup = BeautifulSoup(r)

    articles = soup.find_all(
        lambda tag: any(
            [tag.name == x1 and tag.get(x2) == x3 for x1, x2, x3 in tags]
        )
    )

    urls = []

    for article in articles:

        links = article.find_all("a", href=True)

        for link in links:

            url = urljoin(base_url, link["href"])

            if (
                (url not in urls)
                and (not re.search(links_to_excl, url))
                and (re.search(links_to_incl, url))
            ):

                urls.append(url)

    return urls


def get_article_text(url, tags, in_chunks=False, split_on="\n"):
    """
    Scrape text content from a webpage.

    Args:
        url (str): link to webpage to scrape
        tags (list of tuples): attributes by which to look for relevant text blocks.
            For example, `(div, id, post-123)` means looking for `div` with the
            id post-123.
        in_chunks (bool): whether to look for all occurrences of the tags, or
            just the single instance. Defaults to False
        split_on (str): if a single block of text, how to split into
            chunks/paragraphs. Defaults to '\n'

    Returns:
        list of str: list of text chunks from given webpage
    """

    r = request.urlopen(url).read()
    soup = BeautifulSoup(r)

    if in_chunks:

        raw_text = soup.find_all(
            lambda tag: any(
                [tag.name == x1 and tag.get(x2) == x3 for x1, x2, x3 in tags]
            )
        )

        raw_text_s = [para.getText(separator=" ") for para in raw_text]

    else:

        raw_text = soup.find(
            lambda tag: any(
                [tag.name == x1 and tag.get(x2) == x3 for x1, x2, x3 in tags]
            )
        ).getText(separator=" ")

        raw_text_s = re.split(split_on, raw_text)

    return raw_text_s


if __name__ == "__main__":

    import argparse
    from pathlib import Path
    import json

    parser = argparse.ArgumentParser(description="Scrape website articles")

    parser.add_argument(
        "--config_filepath",
        type=Path,
        default=Path(__file__).absolute().parent / "article_site_configs.json",
        help="Filepath to JSON file containing configs for websites to scrape",
    )

    parser.add_argument(
        "--raw_data_dir",
        type=Path,
        help="Directory for saving raw scraped text",
        default=Path(__file__).absolute().parent / "data" / "raw",
    )

    args = parser.parse_args()

    # Create folders for saving files
    if not args.raw_data_dir.exists():
        args.raw_data_dir.mkdir(parents=True)

    # Sites to scrape and specifications for searching links/text
    with open("article_site_configs.json", "r") as fp:
        site_configs = json.load(fp)

    # The configs should specify the following for each site:
    # base_urls (list of str): links to main article list page
    # tags_main (list of tuples): tags to use to search for article links on
    #   the main page(s).
    #   For example: 'tags_main': [('div', 'class', ['col-sm-4']),
    #                              ('div', 'class', ['col-sm-3'])]
    # links_to_excl (str): regex pattern of links to specifically exclude (optional)
    # links_to_incl (str): regex pattern of links to specifically include (optional)
    # tags_post (list of tuples): tags to use within article pages to extract
    #   the main article text
    # in_chunks (bool): whether to look for all occurrences of the tags (text
    #   is in chunks), or just a single instance
    # split_on (str): regex pattern for how to split text into paragraphs, if
    #   the text is a single block

    # Scrape each site for astrology-related content and clean up texts
    for site in site_configs:

        links = []

        for url in site_configs[site]["base_urls"]:

            links += get_article_links(
                url,
                site_configs[site]["tags_main"],
                site_configs[site]["links_to_excl"],
                site_configs[site]["links_to_incl"],
            )

        for link in links[:100]:  # Max 100 articles from each source

            try:

                raw_text = get_article_text(
                    link,
                    site_configs[site]["tags_post"],
                    site_configs[site]["in_chunks"],
                    site_configs[site]["split_on"],
                )

            except HTTPError as e:

                if e.code == 429:

                    print("Too many requests...waiting to retry")
                    time.sleep(60 * 2)

                    raw_text = get_article_text(
                        link,
                        site_configs[site]["tags_post"],
                        site_configs[site]["in_chunks"],
                        site_configs[site]["split_on"],
                    )

                else:
                    raise Exception(
                        f"HTTPError encountered when trying to scrape {link}"
                    )

            fp_raw = args.raw_data_dir / f"articles_{site}.txt"
            with open(fp_raw, "a", encoding="utf-8") as f:
                f.write("\n".join(raw_text) + "\n")
