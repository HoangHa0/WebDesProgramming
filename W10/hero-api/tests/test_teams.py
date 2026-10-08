def test_create_team_duplicate(client):
    body = {
        "name": "Avengers",
        "headquarters": "New York",
    }

    assert (
        client.post(
            "/api/v1/teams",
            json=body,
        ).status_code
        == 201
    )

    assert (
        client.post(
            "/api/v1/teams",
            json=body,
        ).status_code
        == 409
    )
