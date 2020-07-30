from unittest import TestCase

from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_URL = 'mongodb://localhost:27017/'
TEST_DB = 'cellcomm-test'


class DbTestCase(TestCase):
    def setUp(self):
        client = MongoClient(MONGO_URL)
        client.drop_database(TEST_DB)
        self.__test_db = client[TEST_DB]

    def _coll(self, coll_name) -> Collection:
        return self.__test_db[coll_name]
