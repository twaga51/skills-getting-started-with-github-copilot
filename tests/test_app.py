import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_no_cache_header(client):
    r = client.get("/activities")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)
    # Ensure no caching to reflect live updates
    assert r.headers.get("cache-control") == "no-store"


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    email = "test.user+signup@example.com"

    # Ensure clean start
    if email in activities[activity]["participants"]:
        client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Sign up
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # Duplicate signup should fail
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400

    # Unregister
    r3 = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert r3.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_nonexistent_activity(client):
    r = client.post("/activities/Nonexistent/signup", params={"email": "x@y.z"})
    assert r.status_code == 404


def test_unregister_not_registered(client):
    activity = "Programming Class"
    email = "not.registered@example.com"
    # Ensure not present
    if email in activities[activity]["participants"]:
        client.delete(f"/activities/{activity}/signup", params={"email": email})

    r = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 404
