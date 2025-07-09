from uuid import UUID

import pytest
from fastapi import HTTPException

from src.models.task import Status
from src.schemas.task import TaskWithParticipants, TaskFilters, UpdateTaskRequest
from src.schemas.user import UserDB
from tests.fixtures.db_mocks import TASKS, USERS
from tests.utils import BaseTestCase

TEST_TASK_SERVICE_CREATE_TASK_PARAMS: list[BaseTestCase] = [
    BaseTestCase(
        data=TASKS[0],
        expected_data=[TASKS[0]],
        description="Valid task"
    ),
    BaseTestCase(
        data={
            "id": UUID("48d4cc0f-edcf-4cdc-962b-4752e5338cdf"),
            "title": "First Task",
            "status": Status.todo,
            "author_id": UUID("a02cad63-c8f5-4fab-a759-023cb030caf2")
        },
        expected_error=pytest.raises(HTTPException),
        description="Non-existing author_id"
    ),
    BaseTestCase(
        data={
            "id": UUID("48d4cc0f-edcf-4cdc-962b-4752e5338cdf"),
            "title": "First Task",
            "status": Status.todo,
            "author_id": UUID("a01cad63-c8f5-4fab-a759-023cb030caf2"),
            "assignee_id": UUID("53f181f4-2681-4a37-b05c-af6a2299f8d8")
        },
        expected_error=pytest.raises(HTTPException),
        description="Non-existing assignee_id"
    )
]

TEST_TASK_SERVICE_GET_TASK_WITH_PARTICIPANTS_PARAMS: list[BaseTestCase] = [
    BaseTestCase(
        data={"task_id": UUID("48d4cc0f-edcf-4cdc-962b-4752e5338cdf")},
        expected_data=TaskWithParticipants(
            id=TASKS[0]["id"],
            title=TASKS[0]["title"],
            description=TASKS[0]["description"],
            status=TASKS[0]["status"],
            author_id=TASKS[0]["author_id"],
            assignee_id=TASKS[0]["assignee_id"],
            participants=[UserDB(**USERS[0])]
        ),
        description="Existing task_id"
    ),
    BaseTestCase(
        data={"task_id": UUID("68d4cc0f-edcf-4cdc-962b-4752e5338cdf")},
        expected_error=pytest.raises(HTTPException),
        description="Non-existing task_id"
    ),
]

TEST_TASK_SERVICE_GET_TASKS_BY_FILTERS_PARAMS: list[BaseTestCase] = [
    BaseTestCase(
        data={"filters": TaskFilters(
            ids=[TASKS[0]["id"]],
            status=[Status(TASKS[1]["status"])],
            author_id=None,
            assignee_id=None,
            page=None,
            like="",
            per_page=2
        )},
        expected_data=[],
        description="Filter by id and status"
    ),
    BaseTestCase(
        data={"filters": TaskFilters(
            ids=[TASKS[0]["id"]],
            status=None,
            author_id=None,
            assignee_id=None,
            page=None,
            like="",
            per_page=2
        )},
        expected_data=TASKS[:1],
        description="Filter by id"
    ),
    BaseTestCase(
        data={"filters": TaskFilters(
            ids=None,
            status=None,
            author_id=[TASKS[1]["author_id"]],
            assignee_id=None,
            page=None,
            like="",
            per_page=2
        )},
        expected_data=TASKS[1:],
        description="Filter by author_id"
    ),
    BaseTestCase(
        data={"filters": TaskFilters(
            ids=None,
            status=None,
            author_id=None,
            assignee_id=None,
            page=None,
            like="First",
            per_page=100
        )},
        expected_data=TASKS[:1],
        description="Filter by like"
    ),
    BaseTestCase(
        data={"filters": TaskFilters(
            ids=None,
            status=None,
            author_id=None,
            assignee_id=None,
            page=None,
            like="",
            per_page=1
        )},
        expected_data=TASKS[:1],
        description="Only 1 on page"
    ),
]

TEST_TASK_SERVICE_PARTIAL_UPDATE_TASK_PARAMS: list[BaseTestCase] = [
    BaseTestCase(
        data={
            "task_id": TASKS[0]["id"],
            "task": UpdateTaskRequest(
                title="New First Task",
            )
        },
        expected_data=[{
            "id": TASKS[0]["id"],
            "title": "New First Task",
            "description": TASKS[0]["description"],
            "status": TASKS[0]["status"],
            "author_id": TASKS[0]["author_id"],
            "assignee_id": TASKS[0]["assignee_id"],
            "participants": TASKS[0]["participants"],
        }],
        description="Update task title",
    ),
    BaseTestCase(
        data={
            "task_id": TASKS[0]["id"],
            "task": UpdateTaskRequest(
                title="New First Task",
                description="New First Task Description",
                status=Status.in_progress,
                author_id=UUID("e92c6b7c-a73e-469d-b53f-d5cfef44fb8b"),
                assignee_id=UUID("e38f9be3-7bc0-413c-8033-78feaecc2661")
            )
        },
        expected_data=[{
            "id": TASKS[0]["id"],
            "title": "New First Task",
            "description": "New First Task Description",
            "status": Status.in_progress,
            "author_id": UUID("e92c6b7c-a73e-469d-b53f-d5cfef44fb8b"),
            "assignee_id": UUID("e38f9be3-7bc0-413c-8033-78feaecc2661"),
            "participants": TASKS[0]["participants"],
        }],
        description="Update all fields",
    ),
    BaseTestCase(
        data={
            "task_id": TASKS[0]["id"],
            "task": UpdateTaskRequest()
        },
        expected_error=pytest.raises(HTTPException),
        description="No request body specified",
    ),
    BaseTestCase(
        data={
            "task_id": TASKS[0]["id"],
            "task": UpdateTaskRequest(
                author_id=UUID("a06cad63-c8f5-4fab-a759-023cb030caf2")
            )
        },
        expected_error=pytest.raises(HTTPException),
        description="Non-existing author_id",
    ),
    BaseTestCase(
        data={
            "task_id": TASKS[0]["id"],
            "task": UpdateTaskRequest(
                assignee_id=UUID("a06cad63-c8f5-4fab-a759-023cb030caf2")
            )
        },
        expected_error=pytest.raises(HTTPException),
        description="Non-existing assignee_id"
    ),
    BaseTestCase(
        data={
            "task_id": UUID("48d4cc0f-edcf-5cdc-962b-4752e5338cdf"),
            "task": UpdateTaskRequest(
                title="Non-existing"
            )
        },
        expected_error=pytest.raises(HTTPException),
        description="Non-existing task_id"
    ),
]

TEST_TASK_SERVICE_DELETE_ONE_BY_ID_PARAMS: list[BaseTestCase] = [
    BaseTestCase(
        data={"obj_id": TASKS[0]["id"]},
        expected_data=TASKS[1:],
        description="Existing task_id"
    ),
    BaseTestCase(
        data={"obj_id": UUID("45d4cc0f-edcf-4cdc-962b-4752e5338cdf")},
        expected_error=pytest.raises(HTTPException),
        description="Non-existing task_id"
    ),
]
