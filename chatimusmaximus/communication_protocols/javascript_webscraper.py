import logging
from time import sleep
import threading

from selenium import webdriver


class JavascriptWebscraper(object):

    def __init__(self,
                 url=None,
                 comment_element_id=None,
                 author_class_name=None,
                 message_class_name=None,
                 plugin=None):

        """
        `comment_element_id` is the css element where all the comments are,
        i.e., 'all-comments' for youtube

        `author_class_name` is the css class which holds the comment author
        username i.e., 'yt-user-name' for youtube

        `message_class_name` is the css class which holds the comment test
        ie., 'comment-text' for youtube
        """
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.NOTSET)

        self.url = url
        self._number_of_messages = 0

        self.comment_element_id = comment_element_id
        self.author_class_name = author_class_name
        self.message_class_name = message_class_name
        self.plugin = plugin

        self._thread = threading.Thread(target=self.run_forever)
        self._thread.setDaemon(True)
        self._thread.start()

    def run_forever(self):
        while True:
            try:
                self.log.info('Starting javascript scraper!')
                self.run()
            except Exception as e:
                self.log.exception('Javascript error!', e)

    def run(self):
        self.log.info('starting up phantom javascript!')
        driver = webdriver.PhantomJS()
        # TODO: see if this is needed or not
        driver.set_window_size(1000, 1000)
        driver.get(self.url)

        # NOTE: need some time for comments to load
        self.log.info('youtube sleeping for 5 seconds!')
        sleep(5)
        self.log.info('youtube done sleeping')

        all_comments = driver.find_element_by_id(self.comment_element_id)
        # TODO: add in a signal here that all is connected!

        # NOTE: make sure this is ok if using for anything other than youtube
        comments = all_comments.find_elements_by_tag_name('li')
        self._number_of_messages = len(comments)
        if self.plugin:
            self.plugin.connected_function(True)

        while True:
            sleep(1)
            comments = all_comments.find_elements_by_tag_name('li')
            comments_length = len(comments)

            if comments_length > self._number_of_messages:
                # NOTE: this number is intentionally NEGATIVE
                msgs_not_parsed = self._number_of_messages - comments_length

                self._number_of_messages = len(comments)
                comments = comments[msgs_not_parsed:]
                for comment in comments:
                    find_elem = comment.find_element_by_class_name
                    author = find_elem(self.author_class_name).text

                    message = find_elem(self.message_class_name).text

                    if self.plugin:
                        self.plugin.message_function(author, message)

        if self.plugin:
            self.plugin.connected_function(False)
