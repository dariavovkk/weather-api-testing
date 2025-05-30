import requests

class WeatherClient:
    def __init__(self, api_key, base_url="http://api.openweathermap.org/data/2.5/weather"):
        self.api_key = api_key
        self.base_url = base_url

    def get_weather(self, city, units="metric"):
        params = {'q': city, 'appid': self.api_key, 'units': units}
        return requests.get(self.base_url, params=params)