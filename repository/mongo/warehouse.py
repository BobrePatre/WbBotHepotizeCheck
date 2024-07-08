from pymongo.database import Database


class WarehouseRepo:
    def __init__(self, database: Database):
        self.database: Database = database

    def add_new_article_to_user(self, tg_id: int, article: dict[str, any]):
        self.database.get_collection("articles").insert_one(
            {
                "user_id": tg_id,
                "article": article,
            }
        )

    def get_all_articles(self):
        return list(self.database.get_collection("articles").find({}))


    def get_users_articles(self, tg_id: int):
        res = self.database.get_collection("articles").find({"user_id": tg_id})
        return res

    def get_article(self, article):
        return self.database.get_collection("articles").find_one({"article.article": article})

    def set_new_limit(self, article, new_limit: int):
        self.database.get_collection("articles").update_one(
            {"article.article": article},
            {"$set": {"article.limit": new_limit}},
        )

    def set_new_lower_limit(self, article, new_lower_limit: int):
        self.database.get_collection("articles").update_one(
            {"article.article": article},
            {"$set": {"article.lower_limit": new_lower_limit}},
        )

    def delete_article(self, article):
        self.database.get_collection("articles").delete_many({"article.article": article})
