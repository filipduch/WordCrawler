from sqlalchemy import Column, Integer, BLOB, String, Boolean, BINARY
from hashlib import sha512

from Database import Base
from Encryption import Encryption
from Config import Config


# represents word (id, it's encrypted form and counter)
class WordInfo(Base):
    __tablename__ = "secure_words"

    id = Column(BINARY(64), primary_key=True)
    encrypted_word = Column(BLOB)
    count = Column(Integer)

    def __init__(self, id, encrypted_word, count):
        self.id = id
        self.encrypted_word = encrypted_word
        self.count = count

    def get_word(self):
        return Encryption.decrypt(self.encrypted_word)


# represents word queue item (id, hashed_id, it's encrypted form and counter)
class WordQueueItem(Base):
    __tablename__ = "secure_words_queue"

    id = Column(Integer, primary_key=True)
    hashed_id = Column(BINARY(64))
    encrypted_word = Column(BLOB)
    count = Column(Integer)

    def __init__(self, word, count):
        word_to_hash = str.encode(word + Config['hashing_salt'])
        self.hashed_id = sha512(word_to_hash).digest()
        self.count = count
        self.encrypted_word = Encryption.encrypt(str.encode(word))


# represents information about url sentiment (id, url, is_positive_sentiment - 1, negative - 0)
class UrlInfo(Base):
    __tablename__ = "url_info"

    id = Column(BINARY(64), primary_key=True)
    url = Column(String(255), primary_key=True)
    is_positive_sentiment = Column(Boolean)

    def __init__(self, url):
        url_to_hash = str.encode(url + Config['hashing_salt'])
        self.id = sha512(url_to_hash).digest()
        self.url = url
        self.is_positive_sentiment = True
