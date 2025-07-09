"""Contains tests for task services."""
import pytest

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
        fake_uow_with_users: FakeUnitOfWork,
        case: BaseTestCase,
    ) -> None:
        service = self.__get_service(fake_uow_with_users)
        with case.expected_error:
            task = CreateTaskRequest(**case.data)
            result = await service.create_task(task, task_id=case.data["id"])
            assert compare_dicts_and_models([result], case.expected_data, TaskDB)

    @pytest.mark.parametrize(
        "case", testing_cases.TEST_TASK_SERVICE_GET_TASK_WITH_PARTICIPANTS_PARAMS,
        ids=[case.description for case in testing_cases.TEST_TASK_SERVICE_GET_TASK_WITH_PARTICIPANTS_PARAMS]
    )
    async def test_get_task_with_participants(
        self,
        fake_uow_with_data: FakeUnitOfWork,
        case: BaseTestCase,
    ) -> None:
        service = self.__get_service(fake_uow_with_data)
        with case.expected_error:
            result = await service.get_task_with_participants(**case.data)
            assert result == case.expected_data

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
    ) -> None:
        service = self.__get_service(fake_uow_with_data)
        with case.expected_error:
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
