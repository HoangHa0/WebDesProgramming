import pytest
from fastapi.testclient import TestClient
from app.models import Hero
from app.main import app

client = TestClient(app)


def test_create_hero(client):
    response = client.post(
        "/api/v1/heroes",
        json={
            "name": "Deadpond",
            "secret_name": "Dive Wilson",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "active"
    # Enum -> value

    assert "secret_name" not in response.json()
    # Hidden by response_model


def test_read_hero_not_found(client):
    response = client.get("/api/v1/heroes/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Hero not found"}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": "X"},  # missing fields
        {
            "name": "X",
            "secret_name": "y",
            "age": "old",
        },  # wrong type
        {
            "name": "X",
            "secret_name": "y",
            "age": -5,
        },  # ge=0
        {
            "name": "X",
            "secret_name": "y",
            "status": "dead",
        },  # invalid enum value
    ],
)
def test_create_hero_invalid(client, payload):
    response = client.post(
        "/api/v1/heroes",
        json=payload,
    )

    assert response.status_code == 422


def test_update_hero_partial(session, client):
    hero = Hero(
        name="Tony",
        secret_name="Iron Man",
        age=45,
    )

    session.add(hero)
    session.commit()

    response = client.patch(
        f"/api/v1/heroes/{hero.id}",
        json={
            "status": "retired",
        },
    )

    assert response.json()["age"] == 45
    assert response.json()["status"] == "retired"


def test_hero_unknown_team(client):
    response = client.post(
        "/api/v1/heroes",
        json={
            "name": "Deadpond",
            "secret_name": "Dive Wilson",
            "team_id": 999,
        },
    )

    assert response.status_code == 400
