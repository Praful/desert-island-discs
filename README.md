# webscraper readme
This program scrapes all episode data from the BBC Desert Island Discs website. For each episode, it attempts to get the name of the castaway, the music played, the book chosen, the luxury chosen and the favourite track chosen.

At the time of posting (Feb 2020), over 3,000 episodes were extracted and are in the output directory.

For more information about how I wrote the program, see my blog post: [Desert Island Discs: all the records, books, and luxuries](https://prafulkapadia.com/2020/02/04/desert-island-discs-all-the-records-books-and-luxuries/).

## Installation

The program was tested with Python 3.8 on Windows 10. However, there is nothing intentionally specific to Windows in the program.

The following libraries need to be installed. If you're using `pip`, type:

```
pip install beautifulsoup4
pip install requests
```

## Running

The help is shown below:

```
> python .\scraper.py --help
usage: Desert Island Discs Web Scraper [-h] [--csv OUTPUT] [--start-page START_PAGE] [--end-page END_PAGE] [--sleep SLEEP]

optional arguments:
  -h, --help            show this help message and exit
  --csv OUTPUT          Filename of CSV file (tab-separated). The file will be appended to if it exists (default output is to console)
  --start-page START_PAGE
                        First page to scrape episodes from (default is 1)
  --end-page END_PAGE   Last page to scrape episodes from (default is 1)
  --sleep SLEEP         Time to pause (in seconds) between fetching pages (default is 3 seconds)
```

For example to scrape the first ten pages from the BBC website and store them in a file called `myoutput.csv`, type the following at the command prompt (shell):

```
> python ./scraper.py --end-page 10 --csv myoutput.csv
```

## Unit tests

To run unit tests:

```
> python ./test_episode.py
```

There is also a script that will list out several episodes that have different characteristics. To run it:

```
> python ./list_selective_episodes.py
```

## Output

The complete output of all episodes (at the time of running) are in the output directory. CSV and Excel output files are provided.
