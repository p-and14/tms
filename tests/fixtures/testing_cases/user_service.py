from uuid import UUID

import pytest
from fastapi import HTTPException

from tests.fixtures.db_mocks import USERS
from tests.utils import BaseTestCase

TEST_USER_SERVICE_CREATE_USER_PARAMS: list[BaseTestCase] = [
    BaseTestCase(
        data={
            "id": UUID("a02cad63-c8f5-4fab-a759-023cb030caf2"),
            "full_name": "Egor",
            "email": "egr@example.com",
            "password": "Test_pass123!",
        },
        expected_data=[{
            "id": UUID("a02cad63-c8f5-4fab-a759-023cb030caf2"),
            "full_name": "Egor",
            "email": "egr@example.com",
        }],
        description="Valid user"
    ),
    BaseTestCase(
        data={
            "id": USERS[0]["id"],
            "full_name": USERS[0]["full_name"],
            "email": USERS[0]["email"],
            "password": "Test_pass123!",
        },
        expected_error=pytest.raises(HTTPException),
        description="User with email exists"
    ),
]

TEST_USER_SERVICE_AUTHENTICATE_USER_PARAMS: list[BaseTestCase] = [
    BaseTestCase(
        data={"email": USERS[0]["email"], "password": "Test_pass123!"},
        expected_data=USERS[:1],
        description="Valid user credentials"
    ),
    BaseTestCase(
        data={"email": "error@exp.com", "password": "Test_pass123!"},
        expected_error=pytest.raises(HTTPException),
        description="Incorrect email"
    ),
    BaseTestCase(
        data={"email": USERS[0]["email"], "password": "Pass123!"},
        expected_error=pytest.raises(HTTPException),
        description="Incorrect password"
    ),
]

TEST_USER_SERVICE_GET_JWT_TOKEN_PARAMS: list[BaseTestCase] = [
    BaseTestCase(
        data={"email": USERS[0]["email"], "password": "Test_pass123!"},
        expected_data=USERS[0]["id"].hex,
        description="Valid user credentials"
    ),
]

TEST_USER_SERVICE_GET_CURRENT_USER_PARAMS: list[BaseTestCase] = [
    BaseTestCase(
        data={"claims": {"sub": USERS[0]["id"].hex}},
        expected_data=USERS[:1],
        description="Valid user credentials"
    ),
    BaseTestCase(
        data={"claims": {"sub": UUID("a06cad63-c8f5-4fab-a759-023cb030caf2").hex}, "expire_minutes": 0},
        expected_error=pytest.raises(HTTPException),
        description="Invalid user_id"
    ),
    BaseTestCase(
        data={"claims": {"sub": USERS[0]["id"].hex}, "expire_minutes": 0},
        expected_error=pytest.raises(HTTPException),
        description="Token expired"
    ),
    BaseTestCase(
        data={"token": "invalid-token"},
        expected_error=pytest.raises(HTTPException),
        description="Invalid token"
    )
]
