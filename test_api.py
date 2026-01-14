import requests

BASE_URL = "http://localhost:8082"


def test_get_animations():
    response = requests.get(f"{BASE_URL}/animations")
    assert response.status_code == 200
    animations = response.json()
    assert isinstance(animations, list)
    assert len(animations) > 0
    for animation in animations:
        assert "name" in animation
        assert "module" in animation
        assert "params" in animation


def test_get_animation_schema():
    response = requests.get(f"{BASE_URL}/animations")
    animations = response.json()
    for animation in animations:
        response = requests.get(f"{BASE_URL}/animations/{animation['name']}/schema")
        assert response.status_code == 200
        schema = response.json()
        assert "title" in schema
        assert "type" in schema
        assert "properties" in schema
