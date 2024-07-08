from pymongo.database import Database


class MongoRepository:
    def __init__(self, database: Database):
        self.database = database
        self.collection = database.get_collection(self.__class__.__name__.lower().replace('repository', ''))
