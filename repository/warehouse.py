import logging

from repository.base import MongoRepository


class WarehouseRepository(MongoRepository):
    def add_new_article_to_user(self, tg_id: int, article: dict[str, any]):
        self.collection.insert_one(
            {
                "user_id": tg_id,
                "article": article,
            }
        )

    def get_all_articles(self):
        return list(self.collection.find({}))

    def get_users_articles(self, tg_id: int):
        res = self.collection.find({"user_id": tg_id})
        return res

    def get_article(self, article):
        logging.info("Getting article %s", article)
        return self.collection.find_one({"article.article": article})

    def set_new_limit(self, article, new_limit: int):
        self.collection.update_one(
            {"article.article": article},
            {"$set": {"article.limit": new_limit}},
        )

    def set_new_lower_limit(self, article, new_lower_limit: int):
        self.collection.update_one(
            {"article.article": article},
            {"$set": {"article.lower_limit": new_lower_limit}},
        )

    def delete_article(self, article):
        self.collection.delete_many({"article.article": article})
