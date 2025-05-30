import os
import pytest
import requests
from jsonschema import validate, ValidationError
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise Exception("API_KEY is missing or not loaded!")

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

weather_response_schema = {
    "type": "object",
    "properties": {
        "coord": {
            "type": "object",
            "properties": {
                "lon": {"type": "number"},
                "lat": {"type": "number"},
            },
            "required": ["lon", "lat"]
        },
        "weather": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "main": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["id", "main", "description"]
            }
        },
        "main": {
            "type": "object",
            "properties": {
                "temp": {"type": "number"},
                "pressure": {"type": "number"},
                "humidity": {"type": "number"},
            },
            "required": ["temp", "pressure", "humidity"]
        },
        "name": {"type": "string"},
    },
    "required": ["coord", "weather", "main", "name"]
}

error_response_schema = {
    "type": "object",
    "properties": {
        "cod": {"type": ["string", "number"]},
        "message": {"type": "string"},
    },
    "required": ["cod", "message"]
}

class WeatherClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, city_name):
        params = {'q': city_name, 'appid': self.api_key, 'units': 'metric'}
        return requests.get(BASE_URL, params=params)

@pytest.fixture
def client():
    return WeatherClient(API_KEY)

def test_get_weather_success(client):
    response = client.get_weather("Warsaw")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    try:
        validate(instance=data, schema=weather_response_schema)
    except ValidationError as e:
        assert False, f"Response JSON schema validation failed: {e}"

def test_get_weather_invalid_city(client):
    response = client.get_weather("InvalidCityName")
    assert response.status_code in [404, 200], f"Expected 404 or 200, got {response.status_code}"
    data = response.json()
    if response.status_code == 404:
        validate(instance=data, schema=error_response_schema)

def test_get_weather_empty_city(client):
    response = client.get_weather("")
    assert response.status_code in [400, 404, 401], f"Expected 400, 404 or 401, got {response.status_code}"
    data = response.json()
    if response.status_code in [400, 404, 401]:
        validate(instance=data, schema=error_response_schema)

def test_get_weather_no_city_param():
    response = requests.get(BASE_URL, params={'appid': API_KEY})
    assert response.status_code in [400, 404, 401], f"Expected 400, 404 or 401, got {response.status_code}"
    data = response.json()
    if response.status_code in [400, 404, 401]:
        validate(instance=data, schema=error_response_schema)

def test_get_weather_invalid_api_key():
    wrong_key = "INVALID_KEY"
    params = {'q': 'Warsaw', 'appid': wrong_key, 'units': 'metric'}
    response = requests.get(BASE_URL, params=params)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
    data = response.json()
    validate(instance=data, schema=error_response_schema)