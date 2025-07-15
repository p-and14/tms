"""Contains tests for user services."""

import pytest

from src.schemas.user import CreateUserRequest, UserDB
from src.utils import auth_jwt
from tests.fixtures import FakeUserService, FakeUnitOfWork
from tests.utils import compare_dicts_and_models, BaseTestCase
from tests.fixtures import testing_cases


class TestUserService:
    class _UserService(FakeUserService):
        _repo = "user"

    def __get_service(self, uow: FakeUnitOfWork) -> FakeUserService:
        return self._UserService(uow)

    @pytest.mark.parametrize(
        "case", testing_cases.TEST_USER_SERVICE_CREATE_USER_PARAMS,
        ids=[case.description for case in testing_cases.TEST_USER_SERVICE_CREATE_USER_PARAMS]
    )
    async def test_create_user(
        self,
        fake_uow_with_users: FakeUnitOfWork,
        case: BaseTestCase,
    ) -> None:
        service = self.__get_service(fake_uow_with_users)
        with case.expected_error:
            user = CreateUserRequest(**case.data)
            result = await service.create_user(user, user_id=case.data["id"])
            assert compare_dicts_and_models([result], case.expected_data, UserDB)

    @pytest.mark.parametrize(
        "case", testing_cases.TEST_USER_SERVICE_AUTHENTICATE_USER_PARAMS,
        ids=[case.description for case in testing_cases.TEST_USER_SERVICE_AUTHENTICATE_USER_PARAMS]
    )
    async def test_authenticate_user(
        self,
        fake_uow_with_users: FakeUnitOfWork,
        case: BaseTestCase,
    ) -> None:
        service = self.__get_service(fake_uow_with_users)
        with case.expected_error:
            result = await service.authenticate_user(**case.data)
            assert compare_dicts_and_models([result], case.expected_data, UserDB)

    @pytest.mark.parametrize(
        "case", testing_cases.TEST_USER_SERVICE_GET_JWT_TOKEN_PARAMS,
        ids=[case.description for case in testing_cases.TEST_USER_SERVICE_GET_JWT_TOKEN_PARAMS]
    )
    async def test_get_jwt_token(
        self,
        fake_uow_with_users: FakeUnitOfWork,
        case: BaseTestCase,
    ) -> None:
        service = self.__get_service(fake_uow_with_users)
        with case.expected_error:
            result = await service.get_jwt_token(**case.data)
            assert auth_jwt.decode_jwt(result)["sub"] == case.expected_data

    @pytest.mark.parametrize(
        "case", testing_cases.TEST_USER_SERVICE_GET_CURRENT_USER_PARAMS,
        ids=[case.description for case in testing_cases.TEST_USER_SERVICE_GET_CURRENT_USER_PARAMS]
    )
    async def test_get_current_user(
        self,
        fake_uow_with_users: FakeUnitOfWork,
        case: BaseTestCase,
    ) -> None:
        service = self.__get_service(fake_uow_with_users)
        with case.expected_error:
            token = case.data.get("token")
            if not token:
                token = auth_jwt.encode_jwt(**case.data)
            result = await service.get_current_user(token)
            assert compare_dicts_and_models([result], case.expected_data, UserDB)