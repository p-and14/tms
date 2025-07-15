from uuid import UUID

TASKS = (
    {
        "id": UUID("48d4cc0f-edcf-4cdc-962b-4752e5338cdf"),
        "title": "First Task",
        "description": "First Task Description",
        "status": "todo",
        "author_id": UUID("a01cad63-c8f5-4fab-a759-023cb030caf2"),
        "assignee_id": UUID("53f181f2-2681-4a37-b05c-af6a2299f8d8"),
        "column_id": None,
        "sprint_id": None,
        "board_id": None,
        "group_id": None,
        "participants": [
            {
                "id": UUID("a01cad63-c8f5-4fab-a759-023cb030caf2"),
                "full_name": "Ivanov Ivan Ivanovich",
                "email": "ivanov@example.com",
                "hashed_password": "",
            },
        ]
    },
    {
        "id": UUID("f836e641-ffcb-4f60-915e-2994a4258248"),
        "title": "Second Task",
        "description": "Second Task Description",
        "status": "in_progress",
        "author_id": UUID("e92c6b7c-a73e-469d-b53f-d5cfef44fb8b"),
        "assignee_id": UUID("e38f9be3-7bc0-413c-8033-78feaecc2661"),
        "column_id": None,
        "sprint_id": None,
        "board_id": None,
        "group_id": None,
        "participants": []
    }
)
