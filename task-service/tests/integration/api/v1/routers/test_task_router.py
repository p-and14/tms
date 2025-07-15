"""Contains tests for task routes."""
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from starlette.status import HTTP_404_NOT_FOUND

from src.api.v1.routers.task import TaskService
from tests.fixtures import testing_cases, USERS
from tests.utils import RequestTestCase, prepare_payload


class TestTaskRouter:
    @staticmethod
    @pytest.mark.parametrize(
        "case", testing_cases.TEST_TASK_ROUTE_CREATE_PARAMS,
        ids=[case.description for case in testing_cases.TEST_TASK_ROUTE_CREATE_PARAMS]
    )
    async def test_create_task(
        case: RequestTestCase,
        async_client: AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock = AsyncMock()
        if case.expected_status == 422:
            mock.side_effect = HTTPException(422)
        monkeypatch.setattr(TaskService, "check_user_existence", mock)

        response = await async_client.post(case.url, json=case.data, headers=case.headers)
        assert response.status_code == case.expected_status
        assert prepare_payload(response, ['id']) == case.expected_data


    @staticmethod
    @pytest.mark.parametrize(
        "case", testing_cases.TEST_TASK_ROUTE_GET_ALL_PARAMS,
        ids=[case.description for case in testing_cases.TEST_TASK_ROUTE_GET_ALL_PARAMS]
    )
    async def test_get_all_tasks(
        case: RequestTestCase,
        async_client: AsyncClient
    ):
        response = await async_client.get(case.url, headers=case.headers)
        assert response.status_code == case.expected_status
        assert prepare_payload(response) == case.expected_data

    @staticmethod
    @pytest.mark.parametrize(
        "case", testing_cases.TEST_TASK_ROUTE_DELETE_PARAMS,
        ids=[case.description for case in testing_cases.TEST_TASK_ROUTE_DELETE_PARAMS]
    )
    async def test_delete_task(
        case: RequestTestCase,
        async_client: AsyncClient
    ) -> None:
        response = await async_client.delete(case.url, headers=case.headers)
        task_response = await async_client.get(case.url, headers=case.headers)
        assert response.status_code == case.expected_status
        assert task_response.status_code == HTTP_404_NOT_FOUND
