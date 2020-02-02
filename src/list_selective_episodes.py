"""
Before writing unit tests, I wrote this to list a some episodes that were different from each other. 
"""
from scraper import *
import time

# There are about 200 pages of episde listings. Each page has about 10 episodes.
# Choose a subst to process. Once happy program is working, all pages could be
# processed.
LISTING_START_PAGE=51
LISTING_END_PAGE=150

TEST_PROGRAMME_LISTING_1 = "../data/BBC Radio 4 - Desert Island Discs - Available now.html"

TEST_EPISODE_FILES = [
"../data/BBC Radio 4 - Desert Island Discs, Cilla Black.html",
"../data/BBC Radio 4 - Desert Island Discs, Classic Desert Island Discs_ Freddie Flintoff.html",
"../data/BBC Radio 4 - Desert Island Discs, Isabella Tree, writer and conservationist.html",
"../data/BBC Radio 4 - Desert Island Discs, Sir Malcolm Sargent.html",
"../data/BBC Radio 4 - Desert Island Discs, Michael Lewis, writer.html",
"../data/BBC Radio 4 - Desert Island Discs, Leo McKern.html",
"../data/BBC Radio 4 - Desert Island Discs, Nile Rodgers.html",
"../data/BBC Radio 4 - Desert Island Discs, Wendell Pierce, actor.html",
"../data/BBC Radio 4 - Desert Island Discs, Thom Yorke, musician.html",
]
TEST_EPISODE_URLS = [
    #  'https://www.bbc.co.uk/programmes/p07kj8zf',
    #  'https://www.bbc.co.uk/programmes/b0b7d63p',
    #  'https://www.bbc.co.uk/programmes/p07kj8zf',
    #  'https://www.bbc.co.uk/programmes/b0b42t4h',
    #  'https://www.bbc.co.uk/programmes/b08rpcqb',
    #  'https://www.bbc.co.uk/programmes/b08fdhjs',
    #  'https://www.bbc.co.uk/programmes/b087pl4j',
    #  'https://www.bbc.co.uk/programmes/b03nrpc3',
    #  'https://www.bbc.co.uk/programmes/b01hw633',
    #  'https://www.bbc.co.uk/programmes/b019f6jt',
    #  'https://www.bbc.co.uk/programmes/b011tw7l',
    #  'https://www.bbc.co.uk/programmes/b00y50qk',
    #  'https://www.bbc.co.uk/programmes/b00vc504',
    #  'https://www.bbc.co.uk/programmes/b00dqctb',
    #  'https://www.bbc.co.uk/programmes/p009366t',
    #  'https://www.bbc.co.uk/programmes/p00937l3',
    #  'https://www.bbc.co.uk/programmes/p00947mj',
    #  'https://www.bbc.co.uk/programmes/p009ml01',
    #  'https://www.bbc.co.uk/programmes/b011tw7l',
    #  'https://www.bbc.co.uk/programmes/b019f6jt',
    #  'https://www.bbc.co.uk/programmes/b01hw633',
    #  'https://www.bbc.co.uk/programmes/b03nrpc3'

    'https://www.bbc.co.uk/programmes/b09h0bkl',
    'https://www.bbc.co.uk/programmes/b06rl9s5',
    'https://www.bbc.co.uk/programmes/b0b4zdn9',
    'https://www.bbc.co.uk/programmes/m000dpn1',
    'https://www.bbc.co.uk/programmes/p0783jvd',
    'https://www.bbc.co.uk/programmes/p009368q',
    'https://www.bbc.co.uk/programmes/m00014y2',
    'https://www.bbc.co.uk/programmes/b06d29bf',
]




def testProgrammeListing(listing_page):
    with open(listing_page, "r") as f:
        soup = BeautifulSoup(f.read(), SOUP_PARSER)

    #  print(soup.prettify())
    #

    print(soup.title.text)

    #  printArray(soup.find_all('h2', class_="programme__titles"))

    parser = DesertIslandDiscsParser(soup)
    parser.parse()
    parser.as_csv('./output1.csv')

    #  for c in parser.castaways().values():
        #  print(c.name)
        #  print(c)

#  only_tags_with_id_link2 = SoupStrainer(id="xyz")
#  soup = BeautifulSoup(html_doc, 'html.parser')

#  print(soup.prettify())

def print_episode(e):
    #  if len(e.tracks) < 8: print ('Tracks missing')
    #  if not e.book: print ('Book missing')
    #  if not e.luxury: print ('Luxury missing')
    #  if not e.favourite_track: print ('Favourite track missing')
    print(e)

def test_episode(soup):
    parser = DesertIslandDiscsParser(soup)
    episode = parser.parse_episode(soup)
    print_episode(episode)

def test_episode_url(url):
    print("================================================================================")
    print(f'Processing {url}')
    test_episode(BeautifulSoup(GetPage(url), SOUP_PARSER))

def test_episode_file(filename):
    print("================================================================================")
    print(f'Processing {filename}')
    with open(filename, 'r') as episode_file:
        test_episode(BeautifulSoup(episode_file.read(), SOUP_PARSER))

def testMultiplePages(start_page, end_page):
    parser = DesertIslandDiscsParser()
    for page in range(start_page, end_page+1):
        print(f'Fetching page {page}')
        url = DESERT_ISLAND_DISCS_PAGE % page
        soup = BeautifulSoup(GetPage(url), SOUP_PARSER)
        parser.parse(soup)
        time.sleep(2)


    print('Displaying episodes:')

    parser.as_csv('./output2.csv')
    #  castaways = parser.castaways()
    #  for c in castaways.values():
        #  print('--------------------------------')
        #  print(c.name, c.episode_url)
        #  print_episode(c.episode)

#================================================================================


#TODO this episode has encoding issue when output piping to file
# https://www.bbc.co.uk/programmes/m000c3fc

#  testProgrammeListing(TEST_PROGRAMME_LISTING_1)
#

for file in TEST_EPISODE_FILES:
    test_episode_file(file)

for url in TEST_EPISODE_URLS:
    test_episode_url(url)

#  testMultiplePages(LISTING_START_PAGE, LISTING_END_PAGE)

# listing page
#  https://www.bbc.co.uk/programmes/b006qnmr/episodes/player?page=3
#
#  may need this when writing output to a file; piping output using ">" gives error
#  File "C:\apps\python\latest3-64\lib\encodings\cp1252.py", line 19, in encode
    #  return codecs.charmap_encode(input,self.errors,encoding_table)[0]
#  UnicodeEncodeError: 'charmap' codec can't encode character '\u0107' in position 219: character maps to <undefined>
#  Win 10.
#with open('filename', 'w', encoding='utf-8') as f:
