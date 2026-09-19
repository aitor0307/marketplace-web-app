def test_register_rejects_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Ada",
            "email": "not-an-email",
            "password": "s3cret!",
            "state": "California",
            "city": "Oakland",
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert any(err["loc"] == ["email"] for err in body["message"])


def test_list_listings_query_is_validated(client):
    response = client.get("/api/v1/listings", query_string={"price_min": "not-a-number"})
    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert any(err["loc"] == ["price_min"] for err in body["message"])


def test_list_listings_accepts_blank_filters(client):
    response = client.get("/api/v1/listings", query_string={"condition": "", "price_min": ""})
    assert response.status_code == 200
    assert response.get_json()["listings"] == []
