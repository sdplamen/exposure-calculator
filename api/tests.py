"""FastAPI tests. Same cases as the Django API, so both APIs agree."""
import sys

import pytest
from fastapi.testclient import TestClient

from api.main import app

api = TestClient(app)
URL = "/api/exposure/"


def test_get_solves_shutter():
    data = api.get(URL, params={"light": 12, "aperture": 5.6, "iso": 200}).json()
    assert data["solved"] == "shutter"
    assert data["exact"]["shutter"] == "1/261"
    assert data["camera"]["shutter"] == "1/250"


def test_post_solves_aperture():
    # Sunny 16 rule
    r = api.post(URL, json={"light": 15, "shutter": "1/125", "iso": 100})
    assert r.status_code == 200
    assert r.json()["camera"]["aperture"] == 16


def test_empty_field_means_calculate():
    r = api.get(URL, params={"light": 7, "aperture": 2.8, "shutter": "1/60", "iso": ""})
    assert r.json()["camera"]["iso"] == 400


def test_needs_exactly_one_empty():
    r = api.get(URL, params={"light": 12, "aperture": 5.6})
    assert r.status_code == 400
    assert "__all__" in r.json()["errors"]


@pytest.mark.parametrize("field, params", [
    ("light", {"light": 99, "aperture": 8, "iso": 100}),
    ("aperture", {"light": 12, "aperture": 3.0, "iso": 100}),
    ("shutter", {"light": 12, "shutter": "250", "iso": 100}),
    ("iso", {"light": 12, "aperture": 8, "iso": 150}),
])
def test_rejects_non_standard_values(field, params):
    r = api.get(URL, params=params)
    assert r.status_code == 400
    assert field in r.json()["errors"]


def test_same_answer_as_django(client):
    params = {"light": -2, "aperture": 16, "iso": 100}
    assert api.get(URL, params=params).json() == client.get(URL, params).json()


def test_fastapi_does_not_load_django():
    import subprocess
    code = "import api.main, sys; print('django' in sys.modules)"
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert out.stdout.strip() == "False", out.stderr
