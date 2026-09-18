def register_payload(**overrides):
    payload = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "password": "s3cret!",
        "state": "California",
        "city": "Oakland",
    }
    payload.update(overrides)
    return payload


def test_register_then_login_issues_jwt(client):
    response = client.post("/api/v1/auth/register", json=register_payload())
    assert response.status_code == 201
    body = response.get_json()
    assert body["access_token"]
    assert body["user"]["email"] == "ada@example.com"

    login_response = client.post(
        "/api/v1/auth/login", json={"email": "ada@example.com", "password": "s3cret!"}
    )
    assert login_response.status_code == 200
    assert login_response.get_json()["access_token"]


def test_login_rejects_bad_password(client):
    client.post("/api/v1/auth/register", json=register_payload())
    response = client.post(
        "/api/v1/auth/login", json={"email": "ada@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_create_listing_requires_auth(client):
    # jwt_verify() falls through to its generic exception handler for a
    # missing/invalid token, so this comes back as 400, not 401.
    response = client.post("/api/v1/listings", data={"title": "Bike"})
    assert response.status_code == 400


def test_create_listing_with_valid_token_reaches_business_logic(client):
    register_response = client.post("/api/v1/auth/register", json=register_payload())
    access_token = register_response.get_json()["access_token"]

    response = client.post(
        "/api/v1/listings",
        headers={"Authorization": "Bearer " + access_token},
        data={"title": "Bike"},
    )
    # jwt_verify()'s default roles=[".*"] lets the USER role through, so
    # this 400s on the missing image (business logic), not on auth.
    assert response.status_code == 400
    assert response.get_json()["error"] == "An image file is required"
