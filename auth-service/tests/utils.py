"""Contains helper functions for tests."""
from copy import deepcopy
from typing import Callable, Any, TypeVar, Iterable, Sequence
from contextlib import AbstractContextManager, nullcontext
from uuid import UUID

from requests import Response

from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK

from tests.constants import BASE_ENDPOINT_URL

Check = Callable[[dict[str, Any]], bool]
T = TypeVar("T")


class BaseConfig(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True
    }


class TestDescription(BaseConfig):
    description: str = ""


class TestExpectation(BaseConfig):
    expected_error: AbstractContextManager = nullcontext()
    expected_status: int = HTTP_200_OK
    expected_data: Any = None
    checks: Iterable[Check] | None = None


class BaseTestCase(TestDescription, TestExpectation):
    data: dict | None = None


class RequestTestCase(BaseTestCase):
    url: str = BASE_ENDPOINT_URL
    headers: dict | None = None


async def bulk_save_models(
    session: AsyncSession,
    model: type[DeclarativeBase],
    data: Iterable[dict[str, Any]],
    *,
    commit: bool = False,
) -> None:
    """Bulk saves model objects to the database."""
    for values in data:
        await session.execute(insert(model).values(**values))

    if commit:
        await session.commit()
    else:
        await session.flush()


def compare_dicts_and_models(
    result: Sequence[DeclarativeBase] | Sequence[BaseModel] | None,
    expected_result: Sequence[dict] | None,
    schema: type[BaseModel],
) -> bool:
    """Compares models from the database with expected dictionaries.
    Bring everything to the same Pydantic schema.
    """
    if result is None or expected_result is None:
        return result == expected_result

    result_to_schema = []

    for item in result:
        if isinstance(item, BaseModel):
            result_to_schema = result
            break
        result_to_schema.append(schema(**item.__dict__))

    expected_result_to_schema = [schema(**item) for item in expected_result]

    equality_len = len(result_to_schema) == len(expected_result_to_schema)
    equality_obj = all(obj in expected_result_to_schema for obj in result_to_schema)
    return all((equality_len, equality_obj))


def match_data_to_response_structure(data: dict[str, Any]) -> dict[str, Any]:
    res = deepcopy(data)
    for key, value in res.items():
        if isinstance(value, UUID):
            res[key] = str(value)

    res.pop("participants", None)
    return res


def prepare_payload(response: Response, exclude: Sequence[str] | None = None) -> dict:
    """Extracts the payload from the response."""
    payload = response.json().get("payload")
    if payload is None:
        return {}

    if exclude is None:
        return payload

    for key in exclude:
        payload.pop(key, None)

    return payload
