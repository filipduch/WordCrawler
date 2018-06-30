from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from Config import Config

Base = declarative_base()
mysql_connection_string = "mysql://{0}:{1}@{2}/{3}".format(Config['db_user'], Config['db_pass'],
                                                           Config['db_host'], Config['db_name'])


class Database(object):
    def __init__(self):
        # create engine and build tables if needed
        self.engine = create_engine(mysql_connection_string)
        Base.metadata.bind = self.engine
        Base.metadata.create_all()

    # get all words from the db in decrypted form along with counter
    @staticmethod
    def get_all_words(session):
        from DatabaseModels import WordInfo
        words_results = session.query(WordInfo).order_by(WordInfo.count).all()

        items = []
        for word in words_results:
            item = {
                'word': word.get_word(),
                'count': word.count
            }
            items.append(item)

        return items[::-1]

    # save urlInfo object to the db
    @staticmethod
    def save_url_info(session, url_info):
        if url_info is None:
            return
        session.add(url_info)
        session.commit()

    # add word list to the queue
    @staticmethod
    def add_to_words_queue(session, word_list):
        if not word_list or len(word_list) == 0:
            return
        from DatabaseModels import WordQueueItem
        secure_words = [WordQueueItem(word, count) for word, count in word_list]
        session.add_all(secure_words)
        session.commit()

    # get items from the queue and update their counter or insert as a new row
    @staticmethod
    def update_words_stats(session, rows_per_sec):
        from DatabaseModels import WordQueueItem, WordInfo
        queue_results = session.query(WordQueueItem).limit(rows_per_sec)
        queue_results = [res for res in queue_results]

        # check if there is something to do
        if len(queue_results) == 0:
            return

        # sort the results and grab id's only
        queue_results.sort(key=lambda x: x.hashed_id)
        secure_words_ids = [res.hashed_id for res in queue_results]

        # search for all words that are already in the db
        words_results = session.query(WordInfo).filter(WordInfo.id.in_(secure_words_ids)).order_by(WordInfo.id)
        words_results = [word for word in words_results]

        insert_list = []  # this list will contain objects which don't exist in the db
        index = 0  # save last index so we can do smart searching (better performance)
        for queue_word in queue_results:
            insert = True

            for i, word in enumerate(words_results[index:]):
                # we are working on sorted lists so there is no reason to look further if this condition is satisfied
                if word.id > queue_word.hashed_id:
                    break

                # we have found the word in the db, update it's counter
                if word.id == queue_word.hashed_id:
                    word.count += queue_word.count
                    insert = False
                    index += i + 1
                    break

            # not found - add to the list so we add them all right after the loop
            if insert:
                insert_list.append(WordInfo(queue_word.hashed_id, queue_word.encrypted_word, queue_word.count))

        if len(insert_list) > 0:
            session.add_all(insert_list)

        # delete from the queue
        session.query(WordQueueItem).filter(WordQueueItem.id.in_([res.id for res in queue_results])).delete(synchronize_session='fetch')

        session.commit()
