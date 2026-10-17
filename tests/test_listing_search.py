"""Fuzzy listing search (pg_trgm + unaccent) via GET /api/v1/listings?q=."""
import io

import pytest


@pytest.fixture(autouse=True)
def images_folder(app, tmp_path):
    app.config["IMAGES_FOLDER"] = str(tmp_path)


@pytest.fixture
def seller(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Seller",
            "email": "seller@example.com",
            "password": "s3cret!",
            "state": "Madrid",
            "city": "Madrid",
            "registration_key": "test-registration-key",
        },
    )
    assert response.status_code == 201
    return response.get_json()["access_token"]


@pytest.fixture
def create_listing(client, seller):
    def create(title, body="Works fine", tags=(), condition="Used"):
        response = client.post(
            "/api/v1/listings",
            data={
                "title": title,
                "body": body,
                "condition": condition,
                "price": "50",
                "tags": list(tags),
                "images": [(io.BytesIO(b"fake-image-bytes"), "photo.png")],
            },
            headers={"Authorization": f"Bearer {seller}"},
            content_type="multipart/form-data",
        )
        assert response.status_code == 201, response.get_json()
        return response.get_json()["listing"]["title"]

    return create


def search(client, **params):
    response = client.get("/api/v1/listings", query_string=params)
    assert response.status_code == 200, response.get_json()
    return [listing["title"] for listing in response.get_json()["listings"]]


def test_search_tolerates_typos(client, create_listing):
    create_listing("iPhone 12 Pro")
    create_listing("Mountain bike")
    assert search(client, q="iphnoe") == ["iPhone 12 Pro"]


def test_search_ignores_accents_and_case(client, create_listing):
    create_listing("Lámpara de mesa")
    create_listing("Mountain bike")
    assert search(client, q="LAMPARA") == ["Lámpara de mesa"]
    assert search(client, q="lámpara") == ["Lámpara de mesa"]


def test_search_matches_tags_and_description(client, create_listing):
    create_listing("Mountain bike", tags=["bicicleta"])
    create_listing("Desk lamp", body="Includes a warm LED bulb")
    create_listing("Sofa")
    assert search(client, q="bicicleta") == ["Mountain bike"]
    assert search(client, q="bulb") == ["Desk lamp"]


def test_title_matches_rank_above_description_matches(client, create_listing):
    create_listing("Bike helmet", body="Barely used")
    create_listing("Garage clearout", body="Old bike lights and a pump")
    assert search(client, q="bike") == ["Bike helmet", "Garage clearout"]


def test_search_combines_with_filters(client, create_listing):
    create_listing("Road bike", condition="New")
    create_listing("Kids bike", condition="Used")
    assert search(client, q="bike", condition="New") == ["Road bike"]


def test_blank_search_lists_everything_newest_first(client, create_listing):
    create_listing("Sofa")
    create_listing("Chair")
    assert search(client, q="   ") == ["Chair", "Sofa"]


def test_unrelated_search_finds_nothing(client, create_listing):
    create_listing("Sofa")
    assert search(client, q="telescope") == []
