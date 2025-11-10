"""
=============================================================================
File: scraper.py
Description: Get choices of guests on BBC Radio 4's Desert Island Discs show.
Author: Praful https://github.com/Praful/desert-island-discs
Licence: GPL v3

Notes: This is my first Python program. I wrote it to learn Python. There will
be parts that are not "Pythonic". Please let me know what they are! Thanks
=============================================================================
"""

from bs4 import BeautifulSoup
import requests
import re
import sys
import traceback
import collections
from collections.abc import Sequence
import argparse
import csv
import contextlib
import io
import time
import html
from datetime import datetime

SOUP_PARSER = 'html.parser'
#  SOUP_PARSER = 'lxml'

# When track listing is in long description
DISC_PREFIX = 'DISC '

# Episodes available to listen to:
#  DESERT_ISLAND_DISCS_PAGE = 'https://www.bbc.co.uk/programmes/b006qnmr/episodes/player?page=%s'

# All episodes, available or not
DESERT_ISLAND_DISCS_PAGE = 'https://www.bbc.co.uk/programmes/b006qnmr/episodes/guide?page=%s'

FAVOURITE_INDICATORS = ['castaway\'s choice',
                        'castaway\'s favourite', 'favourite']
DEFAULT_FAVOURITE_INDEX = 2

LUXURY_INDICATOR = ['luxury item', 'luxury']
DEFAULT_LUXURY_INDEX = 1

BOOK_INDICATOR = ['book choice', 'book']
DEFAULT_BOOK_INDEX = 1

TEXT_TRACK_INDICATOR = ['one', 'two', 'three',
                        'four', 'five', 'six', 'seven', 'eight']
CLASS_EPISODE = 'Classic Desert Island Discs:'

# Max tracks that can be chosen by castaway
MAX_TRACKS = 8

# There are about 200 pages of episode listings. Each page has about 10 episodes.
# Choose a subset to process. Once happy program is working, all pages could be
# processed but it's courteous to have a pause between getting each page.
# Defaults:
DEFAULT_LISTING_START_PAGE = 1
DEFAULT_LISTING_END_PAGE = 1
DEFAULT_SLEEP = 3

TAB = '\t'


@contextlib.contextmanager
def smart_open(filename=None, filemode='w'):
    """
    Return handle to file (if specified) or sys output
    From https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely/17603000
    """

    if filename and filename != '-':
        #  fh = open(filename, 'w')
        fh = io.open(filename, newline='', mode=filemode, encoding="utf-8")
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def isBlank(myString):
    return not (myString and myString.strip())


def contains(s, search_for_list, case_sensitive=re.IGNORECASE):
    """
    Return index if s contains any string in search_for_list.
    Return -1 if string not found.
    """
    for i, search_for in enumerate(search_for_list):
        if re.search(search_for, s, case_sensitive):
            return i

    return -1


def GetPage(url):
    """
    Fetch page from web
    """
    def page_found(code):
        return code == 200

    page = requests.get(url)

    if not page_found(page.status_code):
        print(f'Status {page.status_code} for {url}')

    return page.content


def clean_string(s):
    """
    Remove unnecessary characters from beginning and end of s
    """
    if result := s:
        # replace stuff like &amp with &, etc
        result = html.unescape(result)

        result = result.strip(' -:,.–‘’')

        # remove initial <p>
        if match1 := re.search(r'<p>(.*)', result, re.IGNORECASE):
            result = match1.group(1)

        # remove trailing </p>
        if match2 := re.search(r'(.*)</p>', result, re.IGNORECASE):
            result = match2.group(1)

    return result


def print_error(msg, error):
    print(f'{msg}: {str(error)}')
    traceback.print_exc(file=sys.stdout)


class DesertIslandDiscsCastaway:
    """
    Represents the data on a listing of episodes and the episode itself for a castaway.
    """

    def __init__(self, name, job, episode_url, episode):
        self.name = name
        self.episode_url = episode_url
        self.job = job
        self.episode = episode

    def __str__(self):
        return f'Name: {self.name}, job: {self.job}, url: {self.episode_url}, {self.episode}'


class DesertIslandDiscsEpisode:
    """
    Represents data from a single episode ie the choices of a castaway.
    """

    def __init__(self, title, tracks, book, luxury, favourite_track, presenter, broadcast_datetime):
        self.title = title
        self.tracks = tracks
        self.book = book
        self.luxury = luxury
        self.favourite_track = favourite_track
        self.presenter = presenter
        # this is a tuple: (date, time)
        self.broadcast_datetime = broadcast_datetime

    def __str__(self):
        s = f'Title: {self.title}'

        if self.tracks:
            s = s + '\nTracks:\n' + self.tracks.__str__()
        if self.book:
            s = s + '\nBook: ' + self.book
        if self.luxury:
            s = s + '\nLuxury: ' + self.luxury
        if self.favourite_track:
            s = s + '\nFavourite track: ' + self.favourite_track
        if self.presenter:
            s = s + '\nPresenter: ' + self.presenter
        if self.broadcast_datetime:
            s = s + \
                f'\nBroadcast date and time: {self.broadcast_datetime[0]} {self.broadcast_datetime[1]}'

        return s


class Track:
    """
    Struct to store artist and song.
    """

    def __init__(self, artist, song):
        # The double underscore makes the attributes private.
        # Single underscore is (by convention) used for protected attributes.
        # For access we need to provide getters and setters. In this case,
        # we provide getters only via @property decorator.
        self.__artist = artist
        self.__song = song

    @property
    def artist(self): return self.__artist

    @property
    def song(self): return self.__song


class TrackList(Sequence):
    """
    The tracks chosen by a castaway.
    """

    def __init__(self):
        self._listing = []

    def __getitem__(self, i):
        if i < 0 or i > (len(self._listing) - 1):
            raise IndexError(f'Track {i} does not exist')

        return self._listing[i]

    def __len__(self):
        return len(self._listing)

    def add(self, track):
        self._listing.append(track)

    # Obsolete since now we inherit from Sequence class which provides iterator and
    # indexing. Keep for reference on how to create generator.
    #
    #  def listing(self):
        #  """
        #  Return generator to iterate. We could implement an iterable class but this was
        #  quicker and shorter.
        #  """
        #  for track in self._listing:
        #  yield track

    @property
    def is_empty(self):
        return (len(self._listing) == 0)

    def __str__(self):
        result = ''
        for i, track in enumerate(self._listing):
            result += f'{i+1}. {track.artist}: {track.song}\n'

        return result


class DesertIslandDiscsParser:
    """
    This is the main class to extract data from the BBC Desert Island Discs website. Like all web scrapers,
    this class will break if the web site is amended in some ways eg change of CSS classes.
    """

    def __init__(self, soup=None):
        self.soup = soup
        self.all_castaways = {}

    def parse(self, soup=None):
        self.parse_episode_listing(soup)

    def name_and_job(self, s):
        """
        Return castaway's name and job title
        """
        name = ''
        job = ''
        nameAndJob = s.split(', ')

        if len(nameAndJob) > 0:
            name = nameAndJob[0].strip()
            if re.search(fr'^{CLASS_EPISODE}', name, re.IGNORECASE):
                name = name[len(CLASS_EPISODE):]

        if len(nameAndJob) > 1:
            job = nameAndJob[1]

        return clean_string(name), clean_string(job)

    def extract_artist_and_song_from_list(self, track_element, class_='artist'):
        artist = ''
        song = ''
        if track_element:
            # Sometimes there is more than one artist, in which create comma-separated list
            artist_element = track_element.find_all('span', class_)
            for e in artist_element:
                artist += ' & ' if artist else ''
                artist += e.text
                # old method, which assumed there was only one artist
                #  artist_element = track_element.find('span', class_='artist')
                #  artist = artist_element.text if artist_element is not None else ''

            song = track_element.p.span.text if track_element.p.span is not None else ''

        return Track(clean_string(artist), clean_string(song))

    def extract_tracks_from_list(self, soup):
        """
        The episode page has a structured list of episodes usually.
        """

        tracks = TrackList()
        tracks_element = soup.find_all('div', class_='segment__track')
        for track_element in tracks_element:
            try:
                track = self.extract_artist_and_song_from_list(track_element)
                tracks.add(track)
            except Exception as e:
                print_error(
                    f'Ignoring error extracting song/artist from element: {track_element}', e)

        return tracks

    def extract_artist_and_song_from_text(self, s):
        # We're using group names for captured groups
        if re.search(' - ', s, re.IGNORECASE):
            return re.search(r'.*:(?P<artist>.*) - (?P<song>.*)', s)
        elif re.search(' by ', s, re.IGNORECASE):
            return re.search(r'.*:(?P<song>.*) by (?P<artist>.*)', s)

        return False

    def extract_tracks_from_long_description(self, s):
        """
        This is an alternative method of extracting track details. The primary method
        is to extract the tracks from the track list in the episode. If that fails,
        we look for DISC in the long description to see if it's there.
        """

        def add_match():
            song = clean_string(match.group('song'))
            artist = clean_string(match.group('artist'))
            tracks.add(Track(artist, song))

        tracks = TrackList()

        for e in s.split(DISC_PREFIX):
            match = self.extract_artist_and_song_from_text(e)

            if match:
                add_match()
            else:
                # Strip away initial number if it exist and try again
                for search_for in TEXT_TRACK_INDICATOR:
                    if re.search(rf'^{search_for}', e, re.IGNORECASE):
                        song_and_artist = e[len(search_for):]
                        match = self.extract_artist_and_song_from_text(
                            song_and_artist)
                        if match:
                            add_match()
                        else:
                            # There's something odd: just use whatever we've found
                            # for both artist and song
                            song = clean_string(song_and_artist)
                            artist = song
                            tracks.add(Track(artist, song))
                        break

        return tracks

    def extract_item_method_1(self, s, search_for):
        result = ''
        for e in s.split('<br/>'):
            e2 = clean_string(e)

            # Use non-greedy to match the search term up to first colon
            if match := re.search(rf'^{search_for}.*?: (.*)', e2, re.IGNORECASE):
                if match:
                    result = clean_string(match.group(1))
                    break

        return result

    def extract_item_method_2(self, soup, search_for):
        """
        Extract from below track listing
        """

        def extract(h, p):
            if h and h.span and p:
                if re.search(search_for, h.span.text, re.IGNORECASE):
                    return p.text
            return ''

        result = ''

        div_elements = soup.find_all('div', class_='segment__content')
        for div in div_elements:
            # There can be more than one luxury if more than one person is on show
            item = extract(div.h3, div.p)
            if item:
                if result:
                    result += ' / '
                result += item
            else:
                # Sometimes the element is an h4 instead of an h3
                item2 = extract(div.h4, div.p)
                if item2:
                    if result:
                        result += ' / '
                    result += item2

        return result

    def extract_item_method_3(self, soup, search_for):
        """
        Extract from below track listing (alternative)
        """
        result = ''
        div_elements = soup.find('div', class_='segments-list')
        if div_elements:
            li_elements = div_elements.find_all('li')
            for li in li_elements:
                if li.h3 and re.search(search_for, li.h3.text, re.IGNORECASE):
                    h4 = li.find('h4')
                    if h4 and h4.span:
                        result = h4.span.text
                        break

        return result

    def extract_presenter(self, s, castaway):
        """
        Used to find presenter of episode
        """
        def find(s, regex):
            if m := re.findall(regex, s):
                return f'{m[0][0]} {m[0][1]}'
            return None

        # For presenter A B (A=first name, B=second name), we are looking for a string like "Presenter: A B", 'A B's castaway is",
        # "interviewed by A B", "A B talks to", "talks to A B", etc.
        # To minimise chance of non-names, we look for two words that start with uppercase for the presenter.
        # We compare with castaway because for something like "John Doe chats with Jane Doe", either may be the
        # presenter or castaway
        for r in [r'Presenter:?\s+([A-Z]\w+) ([A-Z]\w+)',
                  r'([A-Z]\w+) ([A-Z]\w+)[\'’]s castaway',
                  r'([A-Z]\w+) ([A-Z]\w+) casts away',
                  r'[Ii]nterviewed by ([A-Z]\w+) ([A-Z]\w+)', r'([A-Z]\w+) ([A-Z]\w+) interviews',
                  r'speaking to ([A-Z]\w+) ([A-Z]\w+)',
                  r'([A-Z]\w+) ([A-Z]\w+) talks to ', r'talks to ([A-Z]\w+) ([A-Z]\w+)',
                  r'castaway choices with ([A-Z]\w+) ([A-Z]\w+)',
                  r'([A-Z]\w+) ([A-Z]\w+) chats to', r'(chats to [A-Z]\w+) ([A-Z]\w+)',
                  r'[A-Z]\w+ [A-Z]\w+ joins ([A-Z]\w+) ([A-Z]\w+)']:
            # print(s, r, castaway)
            if name := find(s, r):
                if name not in castaway:
                    return name

        return ''

    def extract_broadcast_datetime(self, soup):
        """
        Extract earliest broadcast date and time.
        """
        date = ''
        time = ''
        try:
            # First try broadcast dates
            if (isodates := soup.find_all('div', class_='broadcast-event__time beta')) is not None:
                dates = [datetime.fromisoformat(
                    d['content']) for d in isodates]
                if len(dates) > 0:
                    dates.sort()
                    date = dates[0].strftime('%Y-%m-%d')
                    time = dates[0].strftime('%H:%M')
            # if we don't have the date at this point, it's because we're processing a
            # classic episode. The date for those is in a different location. There is no
            # time.
            if (date == '') and (date := soup.find('time')) is not None:
                date = date['datetime']

        except Exception as e:
            print_error('Failed to extract broadcast date. Ignoring.', e)

        return date, time

    def extract_favourite(self, soup):
        """
        Sometimes the favourite track is in the long description. Other times, it's a
        heading that appears in the track listing above the favourite track. Here we
        look for the heading then extract whatever track appears beneath it.
        """
        def possible_favourite(element):
            return element.h3 and re.search(FAVOURITE_INDICATORS[DEFAULT_FAVOURITE_INDEX],
                                            element.h3.text, re.IGNORECASE)

        result = ''
        track = Track('', '')

        li_elements = soup.find_all('li', class_='segments-list__item')
        for li in li_elements:
            if possible_favourite(li):
                tracks_element = li.find('div', class_='segment__track')
                if tracks_element:
                    track = self.extract_artist_and_song_from_list(
                        tracks_element)
                else:
                    tracks_element = li.find('div', class_='segment__content')
                    track = self.extract_artist_and_song_from_list(
                        tracks_element, 'title')

                if track:
                    break

        if track.artist and track.song:
            result = f'{track.song} by {track.artist}'
        elif track.artist:
            result = track.artist
        else:
            result = track.song

        return result

    def search_and_extract(self, s, search_for):
        """
        Typically used to find luxury, book or favourite in long description
        """

        #  print(f'{search_for=}')
        if (i := contains(s, search_for)) > -1:
            return self.extract_item_method_1(s, search_for[i])
        else:
            return ''

    def extract_other_data(self, name, soup, tracks):
        """
        This method is very dependent on the structure of the HTML. Since the data isn't structured,
        we sometimes use the whole html string and sometimes we let Soup parse it. This has been
        empirically determined based on the (inconsistent) representation of track, book, favourite track,
        and luxury data.
        """

        book = ''
        luxury = ''
        favourite_track = ''
        presenter = ''
        broadcast_datetime = ''
        new_tracks = tracks

        try:
            paragraph_elements = soup.find_all('p')
            for p in paragraph_elements:
                ptext = p.text
                pstr = p.__str__()

                if tracks.is_empty and re.search(DISC_PREFIX, ptext, re.IGNORECASE):
                    new_tracks = self.extract_tracks_from_long_description(
                        ptext)

                if not luxury:
                    luxury = self.search_and_extract(pstr, LUXURY_INDICATOR)

                if not favourite_track:
                    favourite_track = self.search_and_extract(
                        pstr, FAVOURITE_INDICATORS)
                if not book:
                    book = self.search_and_extract(pstr, BOOK_INDICATOR)

                if not presenter:
                    presenter = self.extract_presenter(pstr, name)

        except Exception as e:
            print_error(
                'Method 1 failed to extract tracks/book/luxury/favourite', e)

        # If we were unsuccessful getting some items, try alternative methods
        try:
            if not book:
                book = self.extract_item_method_2(
                    soup, BOOK_INDICATOR[DEFAULT_BOOK_INDEX])
            if not luxury:
                luxury = self.extract_item_method_2(
                    soup, LUXURY_INDICATOR[DEFAULT_LUXURY_INDEX])
            if not favourite_track:
                favourite_track = self.extract_favourite(soup)
            if not broadcast_datetime:
                broadcast_datetime = self.extract_broadcast_datetime(soup)
        except Exception as e:
            print_error(
                'Method 2 failed to extract book/luxury/favourite/broadcast datetime', e)

        # Try another method
        try:
            if not book:
                book = self.extract_item_method_3(
                    soup, BOOK_INDICATOR[DEFAULT_BOOK_INDEX])
            if not luxury:
                luxury = self.extract_item_method_3(
                    soup, LUXURY_INDICATOR[DEFAULT_LUXURY_INDEX])

        except Exception as e:
            print_error('Method 3 failed to extract book/luxury', e)

        return new_tracks, book, favourite_track, luxury, presenter, broadcast_datetime

    def parse_episode(self, soup, castaway=''):
        """
        Parse the page that contains the episode's details for the castaway, extracting
        the songs picked, favourite track, luxury and book
        """
        episode_title = soup.find('h1').text

        tracks = self.extract_tracks_from_list(soup)

        if isBlank(castaway):
            castaway = episode_title

        # Get other data, including track data (if we were unsuccessful using the
        # first method above).
        tracks, book, favourite_track, luxury, presenter, broadcast_datetime = self.extract_other_data(
            castaway, soup, tracks)

        return DesertIslandDiscsEpisode(episode_title, tracks, book, luxury, favourite_track, presenter, broadcast_datetime)

    def parse_castaway_in_listing(self, castaway):
        """
        Parse a castaway on the episode listing page. Then load the episode page itself
        for the castaway and extract details
        """
        if castaway.a is not None:
            name, job = self.name_and_job(castaway.span.text)
            if name or job:
                episode_url = castaway.a['href']
                episode_element = BeautifulSoup(
                    GetPage(episode_url), SOUP_PARSER)
                episode = self.parse_episode(episode_element, name)

                return DesertIslandDiscsCastaway(name, job, episode_url, episode)
            else:
                print(f'*** No name and job: {castaway.a["href"]}')
        else:
            print(f'***Invalid castaway: {castaway}')

        return None

    def parse_episode_listing(self, soup=None):
        """
        Parse a page that contains a list of episodes and extract each castaway's name,
        job title and the URL that contains the episode's details for the castaway
        """

        # This is an example of the HTML for a castaway:
        #   <h2 class="programme__titles"><a href="https://www.bbc.co.uk/programmes/m000cyvf"
        #   class="br-blocklink__link block-link__target"><span class="programme__title gamma">
        #   <span>Rupert Everett, actor</span></span></a></h2>

        source_soup = soup if soup else self.soup
        if not source_soup:
            print('You to have provide a soup object representing the episode list ' +
                  'at class construction or to the parse_episode_listing method.')
            return

        all_castaway_elements = source_soup.find_all(
            'h2', class_='programme__titles')
        for castaway_element in all_castaway_elements:
            #  print(f'========================================')
            try:
                castaway = self.parse_castaway_in_listing(castaway_element)
                if castaway is not None:
                    # Using name as key doesn't allow for castaways who appear more
                    # than once; use object as key since we don't ever use the key
                    #  self.all_castaways[castaway.name] = castaway
                    self.all_castaways[castaway] = castaway
            except Exception as e:
                print_error(
                    f'ERROR processing castaway: {castaway_element}', e)

    @property
    def castaways(self):
        return self.all_castaways


class CastawayWriter:

    def castaway_as_row(self, c):
        """
        Converts castaway to an array, which maps to a row in a CSV file
        """
        result = []

        result.append(c.name)
        result.append(c.job)
        result.append(c.episode_url)

        result.append(c.episode.title)
        result.append(c.episode.book)
        result.append(c.episode.luxury)
        result.append(c.episode.favourite_track)
        result.append(c.episode.presenter)
        result.append(c.episode.broadcast_datetime[0])
        result.append(c.episode.broadcast_datetime[1])

        for t in c.episode.tracks:
            result.append(t.artist)
            result.append(t.song)

        return result

    def csv_header(self):
        """
        Return header row for CSV file
        """
        result = []
        result.append('Castaway')
        result.append('Job')
        result.append('URL')
        result.append('Episode title')
        result.append('Book')
        result.append('Luxury')
        result.append('Favourite track')
        result.append('Presenter')
        result.append('Date first broadcast')
        result.append('Time first broadcast')
        for i in range(1, MAX_TRACKS + 1):
            result.append(f'Artist {i}')
            result.append(f'Song {i}')

        return result

    def as_csv(self, castaways, filename=None, delim=TAB):
        """
        Create a CSV of episodes scraped
        """
        with smart_open(filename, 'a') as output:
            writer = csv.writer(
                output, delimiter=delim, lineterminator='\r\n')
            writer.writerow(self.csv_header())
            for c in castaways.values():
                writer.writerow(self.castaway_as_row(c))


def setup_command_line():
    """
    Define command line switches
    """
    cmdline = argparse.ArgumentParser(prog='Desert Island Discs Web Scraper')
    cmdline.add_argument('--csv', dest='output',
                         help='Filename of CSV file (tab-separated). The file will be appended '
                         'to if it exists (default output is to console)')
    cmdline.add_argument('--start-page', type=int, default=DEFAULT_LISTING_START_PAGE,
                         help=f'First page to scrape episodes from (default is {DEFAULT_LISTING_START_PAGE})')
    cmdline.add_argument('--end-page', type=int, default=DEFAULT_LISTING_END_PAGE,
                         help=f'Last page to scrape episodes from (default is {DEFAULT_LISTING_START_PAGE})')
    cmdline.add_argument('--sleep', type=int, default=DEFAULT_SLEEP,
                         help=f'Time to pause (in seconds) between fetching pages (default is {DEFAULT_SLEEP} seconds)')
    cmdline.add_argument('--url', dest='url',
                         help='URL of episode to process (e.g. https://www.bbc.co.uk/programmes/m000fx1k). '
                         'If this is provided, all other arguments are ignored. Used for testing.')

    return cmdline


def main():
    """
    Processing begins here if script run directly
    """
    args = setup_command_line().parse_args()

    if args.url:
        print(process_episode_url(args.url))
        sys.exit(0)

    parser = DesertIslandDiscsParser()

    for page in range(args.start_page, args.end_page + 1):
        print(f'Fetching page {page}')
        url = DESERT_ISLAND_DISCS_PAGE % page
        soup = BeautifulSoup(GetPage(url), SOUP_PARSER)
        parser.parse(soup)
        time.sleep(args.sleep)

    print('Creating output:')
    writer = CastawayWriter()
    writer.as_csv(parser.castaways, args.output)


def process_episode_url(url):
    print("================================================================================")
    print(f'Processing {url}')
    parser = DesertIslandDiscsParser()
    return parser.parse_episode(BeautifulSoup(GetPage(url), SOUP_PARSER))


def test():

    # test presenter
    # print(process_episode_url('https://www.bbc.co.uk/programmes/m000fx1k'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/m001c678'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/b07m4gls'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/b09lxn6w'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/b09smnhb'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/b03mckqs'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/b00yhv30'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/p0c133xq'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/p07kjcks'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/p0cspg4q'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/b03z3l2g'))
    # print(process_episode_url('https://www.bbc.co.uk/programmes/b03f87bb'))

    # extra columns after last artist
    #  print(process_episode_url('https://www.bbc.co.uk/programmes/m0011403'))
    pass


#  https://stackoverflow.com/questions/419163/what-does-if-name-main-do
if __name__ == '__main__':
    main()
    # test()
