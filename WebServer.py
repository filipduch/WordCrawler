import os
from threading import Thread, main_thread
import json
from time import sleep
import tornado.ioloop
import tornado.web
from sqlalchemy.orm import sessionmaker, scoped_session

from WordsCrawler import WordsCrawler
from Config import Config
from Database import Database


# queue worker thread
def process_words_queue(session):
    while True:
        if not main_thread().is_alive():
            break
        Database.update_words_stats(session, rows_per_sec=Config['queue_rows_per_sec'])
        session.remove()
        sleep(Config['queue_sleep_seconds'])


# subclass which adds session management
class MyRequestHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = self.application.session

    def on_finish(self):
        self.session.remove()


# called on /admin
class AdminHandler(MyRequestHandler):
    def get(self):
        words_info = Database.get_all_words(self.session)
        self.render(os.path.join(Config['frontend_dir'], 'admin.html'), words_info=words_info)


# called on /
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(os.path.join(Config['frontend_dir'], 'index.html'))


# called on /words
class GetAllWordsHandler(MyRequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/json")
        self.write(json.dumps(Database.get_all_words(self.session)))


# called on /crawl
class CrawlSiteHandler(MyRequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/json")
        url = self.get_query_argument("url")

        if not url.startswith('http://') and not url.startswith('https://'):
            error = {
                'error': 'url should start with http:// or https://'
            }
            return self.write(json.dumps(error))

        word_crawler = WordsCrawler(url)
        words = word_crawler.get_words()
        word_crawler.save_to_db(self.session)
        self.write(json.dumps(words))


# main application class
class Application(tornado.web.Application):
    def __init__(self):
        self.database = Database()
        self.session = scoped_session(sessionmaker(bind=self.database.engine))

        handlers = [
            (r"/", IndexHandler),
            (r"/admin", AdminHandler),
            (r"/crawl", CrawlSiteHandler),
            (r"/words", GetAllWordsHandler),
            (r'/frontend/(.*)', tornado.web.StaticFileHandler, {'path': Config['frontend_dir']}),
        ]

        settings = {
            'debug': False
        }

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    # check if encryption keys exist
    if not os.path.exists(Config['private_key_path']) or not os.path.exists(Config['public_key_path']):
        raise RuntimeError("Please generate encryption keys or correct their paths in Config.py")

    # create the app
    app = Application()
    app.listen(8888)

    # spawn queue worker thread
    queue_processor = Thread(target=process_words_queue, kwargs=dict(session=app.session))
    queue_processor.start()

    tornado.ioloop.IOLoop.current().start()
