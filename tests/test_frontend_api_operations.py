"""The API surface the React frontend relies on in place of the Jinja views."""
import io
import os

import pytest


def register(client, email="ada@example.com", name="Ada"):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": name,
            "email": email,
            "password": "s3cret!",
            "state": "Madrid",
            "city": "Madrid",
            "registration_key": "test-registration-key",
        },
    )
    assert response.status_code == 201
    return response.get_json()


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def post_listing(client, token, title="Bike", tags=("red", "fast"), filenames=("bike.png",), field="images"):
    return client.post(
        "/api/v1/listings",
        data={
            "title": title,
            "body": "Barely used",
            "condition": "Used",
            "price": "120",
            "tags": list(tags),
            field: [(io.BytesIO(b"fake-image-bytes"), filename) for filename in filenames],
        },
        headers=bearer(token),
        content_type="multipart/form-data",
    )


def create_listing(client, token, **kwargs):
    response = post_listing(client, token, **kwargs)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["listing"]


@pytest.fixture(autouse=True)
def images_folder(app, tmp_path):
    app.config["IMAGES_FOLDER"] = str(tmp_path)
    app.config["AVATARS_FOLDER"] = str(tmp_path / "avatars")


def test_user_payloads_never_expose_password_hash(client):
    auth = register(client)
    assert "password_hash" not in auth["user"]
    assert auth["user"]["avatar_url"].startswith("https://www.gravatar.com/avatar/")

    public = client.get(f"/api/v1/users/{auth['user']['id']}").get_json()["user"]
    assert set(public) == {"id", "name", "city", "state", "avatar_url", "last_seen"}


def test_default_avatar_is_not_derived_from_the_email(client):
    ada = register(client, email="ada@example.com", name="Ada")
    other = register(client, email="someone-else@example.com", name="Ada")
    # Same name, different emails: the identicon is the same, so it says nothing about the email.
    assert ada["user"]["avatar_url"] == other["user"]["avatar_url"]


def put_avatar(client, auth, user_id=None, filename="me.png", data=b"fake-image-bytes"):
    return client.put(
        f"/api/v1/users/{user_id or auth['user']['id']}/avatar",
        data={"avatar": (io.BytesIO(data), filename)},
        headers=bearer(auth["access_token"]),
        content_type="multipart/form-data",
    )


def test_avatar_upload_replace_and_remove(app, client):
    auth = register(client)
    first = put_avatar(client, auth)
    assert first.status_code == 200, first.get_json()
    first_src = first.get_json()["user"]["avatar_src"]
    assert first.get_json()["user"]["avatar_url"] == f"/static/avatars/{first_src}"

    second = put_avatar(client, auth, filename="me.jpg").get_json()["user"]
    folder = app.config["AVATARS_FOLDER"]
    assert os.listdir(folder) == [second["avatar_src"]]  # the old file is cleaned up
    public = client.get(f"/api/v1/users/{auth['user']['id']}").get_json()["user"]
    assert public["avatar_url"] == f"/static/avatars/{second['avatar_src']}"

    removed = client.delete(
        f"/api/v1/users/{auth['user']['id']}/avatar", headers=bearer(auth["access_token"])
    ).get_json()["user"]
    assert removed["avatar_src"] is None
    assert removed["avatar_url"].startswith("https://www.gravatar.com/avatar/")
    assert os.listdir(folder) == []


def test_avatar_rejects_other_users_and_non_images(client):
    ada = register(client)
    bob = register(client, email="bob@example.com", name="Bob")
    assert put_avatar(client, ada, user_id=bob["user"]["id"]).status_code == 403
    assert put_avatar(client, ada, filename="evil.svg").status_code == 400
    too_big = put_avatar(client, ada, data=b"x" * (5 * 1024 * 1024 + 1))
    assert too_big.status_code == 400


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


def test_listing_accepts_multiple_images_in_upload_order(client):
    auth = register(client)
    created = create_listing(client, auth["access_token"], filenames=("front.png", "back.png", "side.png"))

    assert [url.rsplit("/", 1)[-1] for url in created["image_urls"]] == ["front0.png", "back0.png", "side0.png"]
    assert created["image_url"] == created["image_urls"][0]

    fetched = client.get(f"/api/v1/listings/{created['id']}").get_json()["listing"]
    assert fetched["image_urls"] == created["image_urls"]


def test_listing_still_accepts_the_legacy_single_image_field(client):
    auth = register(client)
    created = create_listing(client, auth["access_token"], field="image")
    assert len(created["image_urls"]) == 1


def test_listing_rejects_too_many_images(app, client):
    app.config["MAX_LISTING_IMAGES"] = 2
    auth = register(client)
    response = post_listing(client, auth["access_token"], filenames=("a.png", "b.png", "c.png"))
    assert response.status_code == 400
    assert response.get_json()["error"] == "A listing can have at most 2 images"


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


def test_favorites_are_stored_in_user_external_data(client):
    from app.models import User

    seller = register(client, email="seller@example.com", name="Seller")
    buyer = register(client, email="buyer@example.com", name="Buyer")
    first = create_listing(client, seller["access_token"], title="Bike")
    second = create_listing(client, seller["access_token"], title="Lamp")
    headers = bearer(buyer["access_token"])

    added = client.post(f"/api/v1/favorites/{first['id']}", headers=headers)
    assert added.status_code == 201
    assert added.get_json() == {"created": True, "favorite_listing_ids": [first["id"]]}

    again = client.post(f"/api/v1/favorites/{first['id']}", headers=headers)
    assert again.status_code == 200
    assert again.get_json()["created"] is False

    client.post(f"/api/v1/favorites/{second['id']}", headers=headers)
    user = User.get_by_id(buyer["user"]["id"])
    assert user.external_data["favorite_listing_ids"] == [first["id"], second["id"]]

    # Most recently added first.
    listed = client.get("/api/v1/favorites", headers=headers).get_json()["listings"]
    assert [listing["id"] for listing in listed] == [second["id"], first["id"]]

    removed = client.delete(f"/api/v1/favorites/{first['id']}", headers=headers)
    assert removed.get_json() == {"removed": True, "favorite_listing_ids": [second["id"]]}
    assert client.delete(f"/api/v1/favorites/{first['id']}", headers=headers).get_json()[
        "removed"
    ] is False


def test_favoriting_a_missing_listing_is_404(client):
    buyer = register(client)
    response = client.post("/api/v1/favorites/999", headers=bearer(buyer["access_token"]))
    assert response.status_code == 404


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


def test_listings_can_be_filtered_by_exact_tag(client):
    seller = register(client)
    skis = create_listing(client, seller["access_token"], title="Rossignol", tags=("esquis", "pista"))
    create_listing(client, seller["access_token"], title="Salomon", tags=("botas",))

    response = client.get("/api/v1/listings", query_string={"tag": "esquis"})
    assert [listing["id"] for listing in response.get_json()["listings"]] == [skis["id"]]

    # Blank means no filter, like the other query params.
    assert len(client.get("/api/v1/listings", query_string={"tag": ""}).get_json()["listings"]) == 2


def test_feedback_is_emailed_to_the_feedback_address(client, monkeypatch):
    sent = []
    monkeypatch.setattr(
        "app.routes.operations.feedback_ops.send_email",
        lambda subject, recipients, text, html, **kwargs: sent.append((subject, recipients, html, kwargs)),
    )
    auth = register(client)

    response = client.post(
        "/api/v1/feedback",
        json={"kind": "bug", "message": "The <b>map</b> breaks", "page": "/listings/3"},
        headers=bearer(auth["access_token"]),
    )
    assert response.status_code == 202
    [(subject, recipients, html, kwargs)] = sent
    assert subject == "Marketplace bug report from Ada"
    assert recipients == ["feedback@example.com"]
    assert kwargs["reply_to"] == "ada@example.com"
    assert "&lt;b&gt;map&lt;/b&gt;" in html and "/listings/3" in html


def test_feedback_requires_login_and_a_valid_kind(client):
    # jwt_verify answers a missing token with 400 (see app/decorators/auth.py).
    anonymous = client.post("/api/v1/feedback", json={"kind": "bug", "message": "x"})
    assert anonymous.status_code == 400
    assert "JWT" in str(anonymous.get_json())
    auth = register(client)
    response = client.post(
        "/api/v1/feedback", json={"kind": "rant", "message": "x"}, headers=bearer(auth["access_token"])
    )
    assert response.status_code == 400
