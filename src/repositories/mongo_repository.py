import logging
from pymongo.database import Database

from bson import Binary
from bson.objectid import ObjectId
from bson.errors import InvalidId

from src.core.mongo_db import mongo_db


log = logging.getLogger(__name__)


class MongoTaskRepository:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.tasks = db.tasks
    
    def _ids_from_binary_to_uuid(self, data: dict) -> None:
        for k, v in data.items():
            if "id" in k and not isinstance(v, ObjectId):
                data[k] = Binary.as_uuid(v)

    def _ids_from_uuid_to_binary(self, data: dict) -> None:
        for k, v in data.items():
            if "id" in k:
                data[k] = Binary.from_uuid(v)

    def create_task(self, data: dict) -> str | None:
        try:
            self._ids_from_uuid_to_binary(data)
            res = self.tasks.insert_one(data)
            log.info(f"Задача c id={res.inserted_id} успешно добавлена в MongoDB")
            return res.inserted_id
        except Exception as e:
            log.error(f"Ошибка при добавлении задачи: {e}")

    
    def get_task_by_id(self, task_id: str | ObjectId) -> dict | None:
        if isinstance(task_id, str):
            try:
                task_id = ObjectId(task_id)
            except (InvalidId, TypeError) as e:
                log.error(f"Неверный формат task_id={task_id}: {e}")
                return

        try:
            res = self.tasks.find_one({"_id": task_id})

            if res is None:
                log.warning(f"Не удалось получить задачу c id={task_id}")
            else:
                self._ids_from_binary_to_uuid(res)
            return res
        except Exception as e:
            log.error(f"Ошибка при получении задачи с id={task_id}: {e}")
    
    def delete_task(self, task_id: str | ObjectId) -> bool:
        if isinstance(task_id, str):
            try:
                task_id = ObjectId(task_id)
            except (InvalidId, TypeError) as e:
                log.error(f"Неверный формат task_id={task_id}: {e}")
                return False

        try:
            res = self.tasks.delete_one({"_id": task_id})

            log.info(f"Задача c id={task_id} удалена из MongoDB")
            return res.acknowledged
        except Exception as e:
            log.error(f"Ошибка при удалении задачи с id={task_id}: {e}")
        return False
    
    def aggregate_by_tags(self) -> list[dict]:
        """
        :return list: [{'_id': ['tag_1', 'tag_2', n], 'task_count': n}]
        """
        pipeline = [{
            "$group": {
                "_id": "$tags",
                "task_count": {"$sum": 1},
            }
        }]
        tags = self.tasks.aggregate(pipeline)
        return tags.to_list()


mongo_task_repository = MongoTaskRepository(mongo_db)
