from datetime import datetime, timezone
from uuid import uuid4

from src.repositories.mongo_repository import mongo_task_repository, MongoTaskRepository
from src.models.task_model import Status


def mongo_task_case(repository: MongoTaskRepository) -> None:
    data = {
        "title": "Task 1",
        "description": "Do something",
        "status": Status.in_progress.value,
        "tags": [
            "tag 1",
            "tag 2",
            "tag 3",
            "tag 4",
        ],
        "created_at": datetime.now(timezone.utc),
        "author_id": uuid4(),
        "assignee_id": uuid4(),
        "author": {
            "full_name": "Иванов Иван Иванович",
            "email": "ivan@example.ru"
        },
        "some_list": [1, 2, 3]
    }

    create_res = repository.create_task(data)
    print(f"{create_res=}")
    if create_res is not None:
        get_res = repository.get_task_by_id(create_res)
        print(f"{get_res=}")
    
    for val in repository.aggregate_by_tags():
        print(val)
    
    if create_res is not None:
        del_res = repository.delete_task(create_res)
        print(del_res)


if __name__ == "__main__":
    mongo_task_case(mongo_task_repository)
