from app.config.testing import TestingConfig


def test_app_boots_with_testing_config(app):
    assert app.config["ENV"] == TestingConfig.ENV
    assert app.testing is True


def test_index_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Marketplace" in response.data


def test_openapi_spec_lists_operations(client):
    response = client.get("/api/v1/docs")
    assert response.status_code == 200
    spec = response.get_json()
    assert "/api/v1/auth/login" in spec["paths"]
    assert "post" in spec["paths"]["/api/v1/auth/login"]
