from calculator.stops import nearest_aperture, nearest_iso, nearest_shutter
import pytest

BASE = {"aperture": 8, "shutter": "1/125", "iso": 100}

# test_web.py
@pytest.mark.parametrize("url", ["/", "/about/"])
def test_pages_load(client, url):
    assert client.get(url).status_code == 200


def test_page_shows_result(client):
    r = client.get("/", {"light": 12, "aperture": 5.6, "iso": 200})
    assert "1/250" in r.content.decode()


def test_api_solves_shutter(client):
    r = client.get("/api/exposure/", {"light": 12, "aperture": 5.6, "iso": 200})
    data = r.json()
    assert data["solved"] == "shutter"
    assert data["exact"]["shutter"] == "1/261"
    assert data["camera"]["shutter"] == "1/250"


def test_api_solves_aperture(client):
    # Sunny 16 rule: EV 15, ISO 100, 1/125 -> about f/16
    r = client.get("/api/exposure/", {"light": 15, "shutter": "1/125", "iso": 100})
    assert r.json()["camera"]["aperture"] == 16


def test_api_solves_iso(client):
    r = client.get("/api/exposure/", {"light": 7, "aperture": 2.8, "shutter": "1/60"})
    assert r.json()["camera"]["iso"] == 400   # exact 367


def test_out_of_range(client):
    # Moonlight at f/16 ISO 100 needs ~17 minutes -> beyond 30 s
    r = client.get("/api/exposure/", {"light": -2, "aperture": 16, "iso": 100})
    assert r.json()["out_of_range"] is True


def test_needs_exactly_one_empty(client):
    r = client.get("/api/exposure/", {"light": 12, "aperture": 5.6})
    assert r.status_code == 400


def test_bad_shutter(client):
    r = client.get("/api/exposure/", {"light": 12, "shutter": "abc", "iso": 100})
    assert "shutter" in r.json()["errors"]


def test_unknown_light(client):
    r = client.get("/api/exposure/", {"light": 99, "aperture": 8, "iso": 100})
    assert "light" in r.json()["errors"]

# test_stops.py

def test_aperture():
    assert nearest_aperture(11.5) == 11
    assert nearest_aperture(2.83) == 2.8


def test_shutter():
    assert nearest_shutter(1 / 1020) == "1/1000"
    assert nearest_shutter(0.7) == "0.8"   # closer in stops, not in numbers


def test_iso():
    assert nearest_iso(1013) == 1000
    assert nearest_iso(30) == 50      # below the range -> lowest value
