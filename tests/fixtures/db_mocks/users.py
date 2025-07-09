from uuid import UUID

USERS = (
    {
        "id": UUID("a01cad63-c8f5-4fab-a759-023cb030caf2"),
        "full_name": "Ivanov Ivan Ivanovich",
        "email": "ivanov@example.com",
        "hashed_password": "$2b$12$7HC1GX.6PI7H9DkZ50yK8OwV0Z.gqsKeINCXZt5UctPdRF25w4mjK",
    },
    {
        "id": UUID("53f181f2-2681-4a37-b05c-af6a2299f8d8"),
        "full_name": "Petrov Petr Petrovich",
        "email": "petrov@exp.ru",
        "hashed_password": "",
    },
    {
        "id": UUID("e92c6b7c-a73e-469d-b53f-d5cfef44fb8b"),
        "full_name": "Kalinin Dmitry Ilyich",
        "email": "kalinin@example.ru",
        "hashed_password": "",
    },
    {
        "id": UUID("e38f9be3-7bc0-413c-8033-78feaecc2661"),
        "full_name": "Kolesov Mark Leonidovich",
        "email": "kolesov@exp.com",
        "hashed_password": "",
    }
)
