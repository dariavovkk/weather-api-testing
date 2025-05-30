from dotenv import load_dotenv
import os
import requests
import pytest

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise Exception("API_KEY is missing or not loaded! Make sure .env file is present and contains API_KEY.")

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

@pytest.fixture
def client():
    return WeatherClient(API_KEY)

class WeatherClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = BASE_URL

    def get_weather(self, city):
        params = {'q': city, 'appid': self.api_key, 'units': 'metric'}
        return requests.get(self.base_url, params=params)

def test_get_weather_success(client):
    response = client.get_weather("Warsaw")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    assert 'main' in data
    assert 'temp' in data['main']

def test_get_weather_invalid_city(client):
    response = client.get_weather("InvalidCityName")
    assert response.status_code in [404, 200], f"Expected 404 or 200, got {response.status_code}"
    data = response.json()
    if response.status_code == 200:
        assert data['name'].lower() != "invalidcityname", "Unexpected valid response for invalid city"

def test_get_weather_empty_city(client):
    response = client.get_weather("")
    assert response.status_code in [400, 404, 401], f"Expected 400/404/401, got {response.status_code}"

def test_get_weather_no_city_param():
    response = requests.get(BASE_URL, params={'appid': API_KEY})
    assert response.status_code in [400, 404, 401], f"Expected 400/404/401, got {response.status_code}"

def test_get_weather_invalid_api_key():
    wrong_api_key = "INVALID_KEY"
    response = requests.get(BASE_URL, params={'q': 'Warsaw', 'appid': wrong_api_key, 'units': 'metric'})
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"