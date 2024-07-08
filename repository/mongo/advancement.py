from pymongo.database import Database

from repository.mongo.base import MongoRepository


class AdvancementRepository(MongoRepository):

    def set_advancement(self, user_id: int, min_amount: int):
        is_exists = self.collection.find_one({'user_id': user_id})
        if is_exists:
            self.collection.update_one(
                {'user_id': user_id},
                {'$set': {'min_amount': min_amount}},
            )
            return
        self.collection.insert_one(
            {"user_id": user_id, "min_amount": min_amount},
        )

    def get_all_advancements(self):
        return list(self.collection.find({}))

    def get_advancement(self, user_id: int):
        return self.collection.find_one({"tg_id": user_id})
