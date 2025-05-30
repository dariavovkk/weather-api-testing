import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def test_get_weather_success():
    params = {'q': 'Warsaw', 'appid': API_KEY, 'units': 'metric'}
    response = requests.get(BASE_URL, params=params)
    assert response.status_code == 200
    data = response.json()
    assert 'main' in data
    assert 'temp' in data['main']

def test_get_weather_invalid_city():
    params = {'q': 'InvalidCityName', 'appid': API_KEY}
    response = requests.get(BASE_URL, params=params)
    assert response.status_code == 404