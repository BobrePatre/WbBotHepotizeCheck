from repository.base import MongoRepository


class UsersRepository(MongoRepository):

    def create_user(self, tg_id: int):
        is_exists = self.collection.find_one({
            "tg_id": tg_id
        })
        if not is_exists:
            self.collection.insert_one({
                "tg_id": tg_id,
            })

    def save_wb_key(self, tg_id: int, wb_key: str):
        self.collection.update_one(
            {"tg_id": tg_id},
            {"$set": {"wb_key": wb_key}}
        )

    def get_user(self, tg_id: int):
        return self.collection.find_one({"tg_id": tg_id})

    def get_all_users(self):
        return list(self.collection.find({}))
