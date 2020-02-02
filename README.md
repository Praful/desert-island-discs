# webscraper readme
Scrape all episode data from the BBC Desert Island Discs website

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
