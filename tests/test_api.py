import pytest
from fastapi.testclient import TestClient

from app import model
from app.main import app

KEY = "test-key"
client = TestClient(app)


@pytest.fixture(autouse=True)
def api_key_env(monkeypatch):
    monkeypatch.setenv("API_KEY", KEY)


def post(body, key=KEY):
    headers = {"x-api-key": key} if key is not None else {}
    return client.post("/predict", json=body, headers=headers)


def test_predict_ok(fraud_row):
    r = post(fraud_row)
    assert r.status_code == 200
    assert r.json() == model.predict(fraud_row)


def test_missing_key_is_401(legit_row):
    assert post(legit_row, key=None).status_code == 401


def test_wrong_key_is_401(legit_row):
    assert post(legit_row, key="salah").status_code == 401


def test_server_without_api_key_env_rejects(legit_row, monkeypatch):
    monkeypatch.delenv("API_KEY")
    assert post(legit_row, key="").status_code == 500


def test_missing_field_is_422(legit_row):
    del legit_row["income"]
    assert post(legit_row).status_code == 422


def test_unknown_category_is_422(legit_row):
    legit_row["device_os"] = "android"
    assert post(legit_row).status_code == 422


def test_minus_one_sentinel_accepted(legit_row):
    legit_row["bank_months_count"] = -1
    legit_row["session_length_in_minutes"] = -1
    assert post(legit_row).status_code == 200


def test_binary_flag_out_of_range_is_422(legit_row):
    legit_row["email_is_free"] = 2
    assert post(legit_row).status_code == 422


def test_schema_matches_bundle():
    from app.schemas import Application

    assert list(Application.model_fields) == model.bundle["features"]
    props = app.openapi()["components"]["schemas"]["Application"]["properties"]
    for col, cats in model.bundle["categories"].items():
        assert props[col]["enum"] == cats


def test_swagger_documents_api_key():
    assert client.get("/docs").status_code == 200
    schemes = app.openapi()["components"]["securitySchemes"]
    assert any(s.get("name") == "x-api-key" and s.get("in") == "header" for s in schemes.values())


def test_committed_openapi_is_current():
    import json
    import pathlib

    from scripts.export_openapi import build

    committed = json.loads((pathlib.Path(__file__).resolve().parent.parent / "openapi.json").read_text())
    assert committed == build()


def test_non_ascii_key_is_401(legit_row):
    r = client.post("/predict", content=__import__("json").dumps(legit_row), headers={"x-api-key": "kü".encode(), "Content-Type": "application/json"})
    assert r.status_code == 401


def test_nan_value_is_422(legit_row):
    body = __import__("json").dumps(legit_row).replace('"income": 0.1', '"income": NaN')
    r = client.post("/predict", content=body, headers={"x-api-key": KEY, "Content-Type": "application/json"})
    assert r.status_code == 422


def test_health_without_key():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "model_name": "fraud-lgbm", "model_version": model.MODEL_VERSION}


def test_root_shows_health():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == client.get("/health").json()


def test_health_in_swagger():
    assert "get" in app.openapi()["paths"]["/health"]


def test_openapi_lists_servers_for_postman():
    from scripts.export_openapi import build

    assert [s["url"] for s in build()["servers"]] == ["https://fraudguard.yudista.tech", "http://localhost:8000"]


def test_swagger_calls_its_own_host():
    # tanpa servers di app, Swagger memanggil host yang sedang dibuka (tidak kena CORS)
    assert "servers" not in app.openapi()


@pytest.mark.parametrize("path", ["/", "/health"])
def test_health_supports_head_for_uptime_monitors(path):
    r = client.head(path)
    assert r.status_code == 200
    assert r.content == b""
