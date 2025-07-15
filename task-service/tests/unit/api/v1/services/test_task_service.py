"""Contains tests for task services."""
import pytest
from unittest.mock import AsyncMock, patch

from _pytest.raises import RaisesExc
from fastapi import HTTPException

from src.schemas.task import CreateTaskRequest, TaskDB
from tests.fixtures import FakeTaskService, FakeUnitOfWork
from tests.utils import compare_dicts_and_models, BaseTestCase
from tests.fixtures import testing_cases


class TestTaskService:
    class _TaskService(FakeTaskService):
        _repo = "task"

    def __get_service(self, uow: FakeUnitOfWork) -> FakeTaskService:
        return self._TaskService(uow)

    @pytest.mark.parametrize(
        "case", testing_cases.TEST_TASK_SERVICE_CREATE_TASK_PARAMS,
        ids=[case.description for case in testing_cases.TEST_TASK_SERVICE_CREATE_TASK_PARAMS]
    )
    async def test_create_task(
        self,
        empty_fake_uow: FakeUnitOfWork,
        case: BaseTestCase,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service = self.__get_service(empty_fake_uow)
        with case.expected_error as error:
            mock = AsyncMock()
            if error is not None:
                mock.side_effect = HTTPException(422)

            monkeypatch.setattr(self._TaskService, "check_user_existence", mock)
            task = CreateTaskRequest(**case.data)
            result = await service.create_task(task, task_id=case.data["id"])
            assert compare_dicts_and_models([result], case.expected_data, TaskDB)

    @pytest.mark.parametrize(
        "case", testing_cases.TEST_TASK_SERVICE_GET_TASKS_BY_FILTERS_PARAMS,
        ids=[case.description for case in testing_cases.TEST_TASK_SERVICE_GET_TASKS_BY_FILTERS_PARAMS])
    async def test_get_tasks_by_filters(
        self,
        fake_uow_with_data: FakeUnitOfWork,
        case: BaseTestCase,
    ) -> None:
        service = self.__get_service(fake_uow_with_data)
        with case.expected_error:
            result = await service.get_tasks_by_filters(**case.data)
            assert compare_dicts_and_models(result, case.expected_data, TaskDB)

    @pytest.mark.parametrize(
        "case", testing_cases.TEST_TASK_SERVICE_PARTIAL_UPDATE_TASK_PARAMS,
        ids=[case.description for case in testing_cases.TEST_TASK_SERVICE_PARTIAL_UPDATE_TASK_PARAMS]
    )
    async def test_partial_update_task(
        self,
        fake_uow_with_data: FakeUnitOfWork,
        case: BaseTestCase,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service = self.__get_service(fake_uow_with_data)
        with case.expected_error as error:
            mock = AsyncMock()
            if error is not None:
                mock.side_effect = HTTPException(422)

            monkeypatch.setattr(self._TaskService, "check_user_existence", mock)
            result = await service.partial_update_task(**case.data)
            assert compare_dicts_and_models([result], case.expected_data, TaskDB)

    @pytest.mark.parametrize(
        "case", testing_cases.TEST_TASK_SERVICE_DELETE_ONE_BY_ID_PARAMS,
        ids=[case.description for case in testing_cases.TEST_TASK_SERVICE_DELETE_ONE_BY_ID_PARAMS]
    )
    async def test_delete_one_by_id(
        self,
        fake_uow_with_data: FakeUnitOfWork,
        case: BaseTestCase,
    ) -> None:
        service = self.__get_service(fake_uow_with_data)
        with case.expected_error:
            await service.delete_one_by_id(**case.data)
            tasks = fake_uow_with_data.get_tasks()
            assert compare_dicts_and_models(tasks, case.expected_data, TaskDB)
