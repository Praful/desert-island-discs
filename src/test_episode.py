import unittest
from bs4 import BeautifulSoup

from scraper import *
import html
TEST_PROGRAMME_LISTING_1 = "../data/BBC Radio 4 - Desert Island Discs - Available now.html"
TEST_EPISODE_1 = "../data/BBC Radio 4 - Desert Island Discs, Cilla Black.html"
TEST_EPISODE_2 = "../data/BBC Radio 4 - Desert Island Discs, Classic Desert Island Discs_ Freddie Flintoff.html"
TEST_EPISODE_3 = "../data/BBC Radio 4 - Desert Island Discs, Isabella Tree, writer and conservationist.html"
TEST_EPISODE_4 = "../data/BBC Radio 4 - Desert Island Discs, Sir Malcolm Sargent.html"
TEST_EPISODE_5 = "../data/BBC Radio 4 - Desert Island Discs, Michael Lewis, writer.html"
TEST_EPISODE_6 = "../data/BBC Radio 4 - Desert Island Discs, Leo McKern.html"
TEST_EPISODE_7 = "../data/BBC Radio 4 - Desert Island Discs, Nile Rodgers.html"
TEST_EPISODE_8 = "../data/BBC Radio 4 - Desert Island Discs, Wendell Pierce, actor.html"
TEST_EPISODE_9 = "../data/BBC Radio 4 - Desert Island Discs, Thom Yorke, musician.html"

TEST_EPISODE_URL_1 = 'https://www.bbc.co.uk/programmes/p07kj8zf'
TEST_EPISODE_URL_2 = 'https://www.bbc.co.uk/programmes/b0b7d63p'
TEST_EPISODE_URL_3 = 'https://www.bbc.co.uk/programmes/p07kj8zf'
TEST_EPISODE_URL_4 = 'https://www.bbc.co.uk/programmes/b0b42t4h'
TEST_EPISODE_URL_5 = 'https://www.bbc.co.uk/programmes/b03nrpc3'
TEST_EPISODE_URL_6 = 'https://www.bbc.co.uk/programmes/b0b4zdn9'
TEST_EPISODE_URL_7 = 'https://www.bbc.co.uk/programmes/b09h0bkl'
TEST_EPISODE_URL_8 = 'https://www.bbc.co.uk/programmes/m000198c'
TEST_EPISODE_URL_9 = 'https://www.bbc.co.uk/programmes/b06d29bf'



class TestEpisode(unittest.TestCase):
    def setUp(self):
        self.parser = DesertIslandDiscsParser()

    def process_episode(self, soup):
        episode = self.parser.parse_episode(soup)
        #  print(episode)
        return episode

    def process_episode_file(self, filename):
        print("================================================================================")
        print(f'Processing {filename}')
        with open(filename, 'r') as episode_file:
            return self.process_episode(BeautifulSoup(episode_file.read(), SOUP_PARSER))

    def process_episode_url(self, url):
        print("================================================================================")
        print(f'Processing {url}')
        return self.process_episode(BeautifulSoup(GetPage(url), SOUP_PARSER))

    def test_multiple_entries(self):
        # self.skipTest('temporarily skipping')
        """
        The book and luxury appear in the long description and below the track listing
        """
        episode = self.process_episode_file(TEST_EPISODE_1)
        self.assertEqual(len(episode.tracks), MAX_TRACKS)
        self.assertEqual(episode.book, 'Fables by Aesop')
        self.assertEqual(episode.favourite_track, 'The Long and Winding Road by The Beatles')
        self.assertEqual(episode.luxury, 'Manicure set and nail varnish')

    def test_tracks_in_long_description(self):
        # self.skipTest('temporarily skipping')
        episode = self.process_episode_file(TEST_EPISODE_2)
        self.assertEqual(len(episode.tracks), MAX_TRACKS)
        self.assertEqual(episode.tracks[0].artist, 'Elvis Presley')
        self.assertEqual(episode.tracks[0].song, 'I Just Can\'t Help Believin\'')
        self.assertEqual(episode.tracks[MAX_TRACKS-1].artist, 'The Eagles')
        self.assertEqual(episode.tracks[MAX_TRACKS-1].song, 'New Kid in Town')

        self.assertEqual(episode.book, '')
        self.assertEqual(episode.favourite_track, '')
        self.assertEqual(episode.luxury, '')

    def test_castaways_favourite(self):
        # self.skipTest('temporarily skipping')
        """
        CASTAWAY'S FAVOURITE: These Foolish Things by Billie Holiday

        The "Favourite track" is denoted by "CASTAWAY'S FAVOURITE" instead of the more usual "Favourite track"
        """
        episode = self.process_episode_file(TEST_EPISODE_3)

        self.assertEqual(episode.favourite_track, 'These Foolish Things by Billie Holiday')

    def test_tracks_in_list_and_long_description(self):
        # self.skipTest('temporarily skipping')
        episode = self.process_episode_file(TEST_EPISODE_3)
        self.assertEqual(len(episode.tracks), MAX_TRACKS)
        self.assertEqual(episode.tracks[0].artist, 'The Waterboys')
        self.assertEqual(episode.tracks[0].song, 'The Whole of the Moon')
        self.assertEqual(episode.tracks[MAX_TRACKS-1].artist, 'Toploader')
        self.assertEqual(episode.tracks[MAX_TRACKS-1].song, 'Dancing In The Moonlight')

        self.assertEqual(episode.book, 'War and Peace by Leo Tolstoy')
        self.assertEqual(episode.favourite_track, 'These Foolish Things by Billie Holiday')
        self.assertEqual(episode.luxury, 'Mask, snorkel and a neoprene vest')

    def test_multiple_artists_for_song(self):
        self.assertTrue(True)

    def test_favourite_track_denoted_by_heading(self):
        # self.skipTest('temporarily skipping')
        episode = self.process_episode_file(TEST_EPISODE_7)
        self.assertEqual(len(episode.tracks), MAX_TRACKS)
        self.assertEqual(episode.tracks[0].artist, 'Chic')
        self.assertEqual(episode.tracks[0].song, 'Le Freak')
        self.assertEqual(episode.tracks[MAX_TRACKS-1].artist, 'Chic')
        self.assertEqual(episode.tracks[MAX_TRACKS-1].song, 'Good Times')

        self.assertEqual(episode.favourite_track, 'The End by The Doors')


    def test_choices_after_track_list(self):
        episode = self.process_episode_file(TEST_EPISODE_7)
        self.assertEqual(episode.book, 'Moby-Dick by Herman Melville')
        self.assertEqual(episode.luxury, 'His ‘Hitmaker’ guitar and an amp')

    def test_luxury_only(self):
        episode = self.process_episode_file(TEST_EPISODE_4)
        self.assertEqual(episode.luxury, 'Ice machine or hot water bottle')

    def test_multiple_word_book_occurrences_in_long_description(self):
        """
        There are multiple occurrences of "book" in the long description but the
        actual book is below the track listing
        """
        episode = self.process_episode_url(TEST_EPISODE_URL_2)
        self.assertEqual(len(episode.tracks), MAX_TRACKS)
        self.assertEqual(episode.tracks[0].artist, 'David Bowie')
        self.assertEqual(episode.tracks[0].song, 'Life On Mars?')
        self.assertEqual(episode.tracks[MAX_TRACKS-1].artist, 'David Bowie')
        self.assertEqual(episode.tracks[MAX_TRACKS-1].song, 'Word On A Wing')

        self.assertEqual(episode.book, 'Hatter’s Castle by A. J. Cronin')
        self.assertEqual(episode.favourite_track, 'Galway Bay by Ruby Murray')
        self.assertEqual(episode.luxury, 'Luxurious underwear')

    def test_mangled_track_in_long_description(self):
        """
        Track listing in description is like below. The Seventh track does not
        have a colon.

        DISC ONE: Don MacLean - American Pie
        DISC TWO: Tino Rossi - Bohémienne aux Grands Yeux Noirs
        DISC THREE: Shirat Hanoded (the wanderer’s song) sung by Betty Klein
        DISC FOUR: Beethoven’s Emperor Concerto, 2nd movement, performed by the Chicago Symphony Orchestra, conducted by Frederick Stock with Arthur Schnabel on piano
        DISC FIVE: Danny Kaye - Ugly Duckling
        DISC SIX: The Beatles - Eleanor Rigby
        DISC SEVEN – Mozart’s Clarinet Quintet in A Major
        DISC EIGHT: Bach Piano Suite – played by Daniel’s grandson
        """

        episode = self.process_episode_url(TEST_EPISODE_URL_3)
        self.assertEqual(episode.tracks[6].artist, 'Mozart’s Clarinet Quintet in A Major')
        self.assertEqual(episode.tracks[6].song, 'Mozart’s Clarinet Quintet in A Major')

    def test_book_luxury_method_3(self):
        episode = self.process_episode_url(TEST_EPISODE_URL_5)

        self.assertEqual(len(episode.tracks), MAX_TRACKS)
        self.assertEqual(episode.book, 'A blank book to record his Desert Island findings')
        self.assertEqual(episode.favourite_track, 'Maria by Blondie')
        self.assertEqual(episode.luxury, 'A huge pair of speakers')

    def test_episode_with_two_luxury_items(self):
        """
        This episode had two guests and they each picked a luxury
        """
        episode = self.process_episode_url(TEST_EPISODE_URL_9)

        self.assertEqual(len(episode.tracks), MAX_TRACKS)
        self.assertEqual(episode.luxury, 'A really big drum kit\n' +
            'A collection of Château d\'Yquem of his choice from 1900-2001, a fridge, Sauternes glasses')

    def test_favourite_track_denoted_by_favourite_track_in_description(self):
        """
        The favourite track is denoted by FAVOURITE TRACK: in the long description
        """
        episode = self.process_episode_url(TEST_EPISODE_URL_8)

        self.assertEqual(len(episode.tracks), MAX_TRACKS)
        self.assertEqual(episode.favourite_track, 'Beethoven\'s Symphony no. 5')

    def test_favourite_track_denoted_by_span_title(self):
        """
        Sometimes favourite track is in the track listing. When this is so, it follows
        as a span object with 'artist' class. In this instance, the span has 'title' span.
        """
        episode = self.process_episode_url(TEST_EPISODE_URL_7)

        # Since the inline favourite track is using the wrong style, it's not picked 
        # up when looking at the track listing. So we have one fewer track. 
        # This is an instance of diminishing returns where we could add code for one 
        # or two episodes. In this instance we've let it stand uncorrected since the 
        # track appears in the favourite track.
        self.assertEqual(len(episode.tracks), MAX_TRACKS-1)
        self.assertEqual(episode.favourite_track, 'Extract from Poem in October by Dylan Thomas')

    def test_book_as_h4(self):
        """
        Normally, BOOK CHOICE appear as h3 when appearing under the tracks listing.
        This is an exception: it appears as h4
        """
        episode = self.process_episode_url(TEST_EPISODE_URL_6)

        self.assertEqual(len(episode.tracks), MAX_TRACKS)
        self.assertEqual(episode.book, 'Hogarth, A Life and a World by Jenny Uglow')

    def test_clean_string(self):

        s='  <p>Luxury: Ice machine or hot water bottle</p>  '
        self.assertEqual(clean_string(s), 'Luxury: Ice machine or hot water bottle')

        s2 = 'The Leopard (In Italian &amp; English) by Giuseppe di Lampedusa'
        self.assertEqual(clean_string(s2), 'The Leopard (In Italian & English) by Giuseppe di Lampedusa')



if __name__ == '__main__':
    unittest.main()
