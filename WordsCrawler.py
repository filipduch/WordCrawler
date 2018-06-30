import requests
import re
from collections import Counter
from bs4 import BeautifulSoup
from bs4.element import Comment
from wit import Wit

from Database import Database
from DatabaseModels import UrlInfo
from Config import Config


class WordsCrawler(object):
    def __init__(self, url):
        self._url = url
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
        }
        self._top_words = []
        self._common_words_num = Config['common_words_num']
        self._url_info = None

    @staticmethod
    def _is_tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False

        if isinstance(element, Comment):
            return False

        return True

    def get_words(self):
        request = requests.get(self._url, headers=self._headers)
        # add content length check too? so we won't process HUGE text traps...
        if request.status_code != 200:
            raise RuntimeError("Invalid status code: {}".format(request.status_code))

        soup = BeautifulSoup(request.text, "html.parser")
        visible_texts = filter(self._is_tag_visible, soup.findAll(text=True))

        words = []
        for text in visible_texts:
            # remove redundant whitespaces and convert to lower case
            text = text.strip().lower()
            if len(text) > 0:
                words.append(text)

        text = u" ".join(words)
        self._find_sentiment(text)

        # find words boundaries
        word_list = re.findall(r'\b\w+', text)
        # count words and get the most common ones
        self._top_words = Counter(word_list).most_common(self._common_words_num)

        cols = ("word", "count")
        # return list of dicts with keys word and count
        return list(map(lambda item: dict(zip(cols, item)), self._top_words))

    def _find_sentiment(self, text):
        wit_client = Wit(Config['wit_access_token'])
        # texts = text.split('.')
        # for text in texts:
        #     if len(text) < 3:
        #         continue
        #     print("len: {}".format(len(text)))
        #     wit_reply = wit_client.message(text)
        self._url_info = UrlInfo(self._url)

    # save url info and top words to database
    def save_to_db(self, session):
        Database.add_to_words_queue(session, self._top_words)
        Database.save_url_info(session, self._url_info)
