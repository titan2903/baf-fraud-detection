import hashlib

import pytest

from app import model


def test_predict_legit_row(legit_row):
    out = model.predict(legit_row)
    assert set(out) == {"model_name", "model_version", "fraud_score", "is_fraud", "threshold"}
    assert out["fraud_score"] == pytest.approx(0.0004747192380841404, rel=1e-6)
    assert out["is_fraud"] is False
    assert out["threshold"] == pytest.approx(0.05602959700862982)
    assert out["model_name"] == "fraud-lgbm"


def test_predict_fraud_row(fraud_row):
    out = model.predict(fraud_row)
    assert out["fraud_score"] == pytest.approx(0.3879462306025753, rel=1e-6)
    assert out["is_fraud"] is True


def test_model_version_is_file_hash():
    assert model.MODEL_VERSION == hashlib.sha256(model.MODEL_PATH.read_bytes()).hexdigest()[:12]


def test_key_order_does_not_matter(legit_row):
    shuffled = dict(reversed(list(legit_row.items())))
    assert model.predict(shuffled)["fraud_score"] == model.predict(legit_row)["fraud_score"]


def test_output_types_are_json_native(fraud_row):
    out = model.predict(fraud_row)
    assert type(out["fraud_score"]) is float and type(out["is_fraud"]) is bool
