from uuid import UUID

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
)

from tests.constants import BASE_ENDPOINT_URL
from tests.utils import RequestTestCase, match_data_to_response_structure
from tests.fixtures.db_mocks import TASKS, USERS

TEST_TASK_ROUTE_CREATE_PARAMS: list[RequestTestCase] = [
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/",
        headers={},
        data={
            "title": "New Task",
            "status": "in_progress",
            "author_id": USERS[0]["id"].hex,
        },
        expected_status=HTTP_201_CREATED,
        expected_data={
            "title": "New Task",
            "status": "in_progress",
            "author_id": str(USERS[0]["id"]),
            "assignee_id": None,
            "board_id": None,
            "column_id": None,
            "description": None,
            "group_id": None,
            "sprint_id": None
        },
        description='Positive case',
    ),
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/",
        headers={},
        data={},
        expected_status=HTTP_422_UNPROCESSABLE_ENTITY,
        expected_data={},
        description="Not valid request body",
    ),
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/",
        headers={},
        data={
            "title": "New Task",
            "status": "invalid-status",
            "author_id": USERS[0]["id"].hex,
        },
        expected_status=HTTP_422_UNPROCESSABLE_ENTITY,
        expected_data={},
        description="Invalid status in data",
    ),
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/",
        headers={},
        data={
            "title": "New Task",
            "status": "todo",
            "author_id": UUID("a06cad63-c8f5-4fab-a759-023cb030caf2").hex,
        },
        expected_status=HTTP_422_UNPROCESSABLE_ENTITY,
        expected_data={},
        description="Invalid author_id in data",
    ),
]

TEST_TASK_ROUTE_GET_ALL_PARAMS: list[RequestTestCase] = [
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/",
        headers={},
        expected_status=HTTP_200_OK,
        expected_data=[
            match_data_to_response_structure(TASKS[0]),
            match_data_to_response_structure(TASKS[1]),
        ],
        description="All tasks",
    ),
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/?ids={TASKS[0]['id']}",
        headers={},
        expected_status=HTTP_200_OK,
        expected_data=[match_data_to_response_structure(TASKS[0])],
        description="Tasks with query param ids",
    ),
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/?status={TASKS[1]['status']}",
        headers={},
        expected_status=HTTP_200_OK,
        expected_data=[
            match_data_to_response_structure(TASKS[1]),
        ],
        description="Tasks with query param status",
    ),
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/?author_id={TASKS[0]['author_id']}&assignee_id={TASKS[1]['assignee_id']}",
        headers={},
        expected_status=HTTP_200_OK,
        expected_data=[],
        description="Tasks with query param author_id and assignee_id",
    ),
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/?page=0&per_page=1",
        headers={},
        expected_status=HTTP_200_OK,
        expected_data=[
            match_data_to_response_structure(TASKS[0]),
        ],
        description="Tasks with query param page and per_page",
    ),
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/?author_id=a07cad63-c8f5-4fab-a759-023cb030caf2",
        headers={},
        expected_status=HTTP_200_OK,
        expected_data=[],
        description="Tasks with incorrect query param author_id",
    )
]

TEST_TASK_ROUTE_DELETE_PARAMS: list[RequestTestCase] = [
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/{TASKS[0]['id']}",
        headers={},
        expected_status=HTTP_204_NO_CONTENT,
        expected_data=[],
        description="Positive case",
    ),
    RequestTestCase(
        url=f"{BASE_ENDPOINT_URL}/tasks/49d4cc0f-edcf-4cdc-962b-4752e5338cdf",
        headers={},
        expected_status=HTTP_404_NOT_FOUND,
        expected_data=[],
        description="Incorrect task_id",
    ),
]