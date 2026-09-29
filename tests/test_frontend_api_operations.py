"""The API surface the React frontend relies on in place of the Jinja views."""
import io

import pytest


def register(client, email="ada@example.com", name="Ada"):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "password": "s3cret!", "state": "Madrid", "city": "Madrid"},
    )
    assert response.status_code == 201
    return response.get_json()


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def create_listing(client, token, title="Bike", tags=("red", "fast")):
    response = client.post(
        "/api/v1/listings",
        data={
            "title": title,
            "body": "Barely used",
            "condition": "Used",
            "price": "120",
            "tags": list(tags),
            "image": (io.BytesIO(b"fake-image-bytes"), "bike.png"),
        },
        headers=bearer(token),
        content_type="multipart/form-data",
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["listing"]


@pytest.fixture(autouse=True)
def images_folder(app, tmp_path):
    app.config["IMAGES_FOLDER"] = str(tmp_path)


def test_user_payloads_never_expose_password_hash(client):
    auth = register(client)
    assert "password_hash" not in auth["user"]
    assert auth["user"]["avatar_url"].startswith("https://www.gravatar.com/avatar/")

    public = client.get(f"/api/v1/users/{auth['user']['id']}").get_json()["user"]
    assert "password_hash" not in public


def test_me_returns_the_token_owner(client):
    auth = register(client)
    response = client.get("/api/v1/auth/me", headers=bearer(auth["access_token"]))
    assert response.status_code == 200
    assert response.get_json()["user"]["email"] == "ada@example.com"


def test_refresh_issues_a_new_access_token_only_for_refresh_tokens(client):
    auth = register(client)

    response = client.post("/api/v1/auth/refresh", headers=bearer(auth["refresh_token"]))
    assert response.status_code == 200
    new_token = response.get_json()["access_token"]
    assert client.get("/api/v1/auth/me", headers=bearer(new_token)).status_code == 200

    rejected = client.post("/api/v1/auth/refresh", headers=bearer(auth["access_token"]))
    assert rejected.status_code == 400


def test_listing_payload_carries_image_author_and_tags(client):
    auth = register(client)
    created = create_listing(client, auth["access_token"])

    assert created["tags"] == ["red", "fast"]
    assert created["image_url"].startswith("/static/listing_images/bike")
    assert created["author"]["id"] == auth["user"]["id"]
    assert created["author"]["name"] == "Ada"

    listed = client.get("/api/v1/listings").get_json()["listings"]
    assert [listing["id"] for listing in listed] == [created["id"]]
    assert listed[0]["author"]["name"] == "Ada"


def test_user_listings_are_public(client):
    auth = register(client)
    created = create_listing(client, auth["access_token"])

    response = client.get(f"/api/v1/users/{auth['user']['id']}/listings")
    assert response.status_code == 200
    assert [listing["id"] for listing in response.get_json()["listings"]] == [created["id"]]


def test_favorites_are_visible_to_their_owner_only(client):
    seller = register(client, email="seller@example.com", name="Seller")
    buyer = register(client, email="buyer@example.com", name="Buyer")
    listing = create_listing(client, seller["access_token"])

    client.post(f"/api/v1/favorites/{listing['id']}", headers=bearer(buyer["access_token"]))

    own = client.get(
        f"/api/v1/users/{buyer['user']['id']}/favorites", headers=bearer(buyer["access_token"])
    )
    assert own.status_code == 200
    assert [fav["id"] for fav in own.get_json()["listings"]] == [listing["id"]]

    other = client.get(
        f"/api/v1/users/{buyer['user']['id']}/favorites", headers=bearer(seller["access_token"])
    )
    assert other.status_code == 403


def test_messages_list_follows_profile_visibility_rules(client, monkeypatch):
    monkeypatch.setattr("app.routes.operations.messages_ops.send_email", lambda *a, **k: None)
    alice = register(client, email="alice@example.com", name="Alice")
    bob = register(client, email="bob@example.com", name="Bob")
    carol = register(client, email="carol@example.com", name="Carol")
    listing = create_listing(client, bob["access_token"])

    client.post(
        f"/api/v1/users/{bob['user']['id']}/messages",
        json={"subject": "Hi", "body": "Still available?", "listing_id": listing["id"]},
        headers=bearer(alice["access_token"]),
    )
    client.post(
        f"/api/v1/users/{carol['user']['id']}/messages",
        json={"subject": "Hey", "body": "Unrelated"},
        headers=bearer(alice["access_token"]),
    )

    # Own id: everything Alice sent or received.
    mine = client.get(
        f"/api/v1/users/{alice['user']['id']}/messages", headers=bearer(alice["access_token"])
    ).get_json()["messages"]
    assert {m["subject"] for m in mine} == {"Hi", "Hey"}

    # Another id: only the conversation between the two of them.
    with_alice = client.get(
        f"/api/v1/users/{alice['user']['id']}/messages", headers=bearer(bob["access_token"])
    ).get_json()["messages"]
    assert [m["subject"] for m in with_alice] == ["Hi"]
    assert with_alice[0]["sender"]["name"] == "Alice"
    assert with_alice[0]["listing"] == {"id": listing["id"], "title": "Bike"}


def test_views_are_marked_deprecated_with_spa_successor(app, client):
    app.config["FRONTEND_URL"] = "https://app.example.com/"
    response = client.get("/login")
    assert response.headers["Deprecation"] == "true"
    assert response.headers["Link"] == '<https://app.example.com/login>; rel="successor-version"'

    api_response = client.get("/api/v1/listings")
    assert "Deprecation" not in api_response.headers


def test_api_allows_the_configured_frontend_origin(client):
    response = client.get("/api/v1/listings", headers={"Origin": "http://localhost:5173"})
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
