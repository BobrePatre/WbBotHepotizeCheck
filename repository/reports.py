from repository.base import MongoRepository


# TODO: Add logic to working with database for managing items in unit economic
class ReportsRepository(MongoRepository):

    def add_item(self, item, user_id):
        item["user_id"] = user_id
        self.collection.insert_one(item)

    def clear_items(self, user_id):
        self.collection.delete_many({"user_id": user_id})
