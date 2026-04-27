from clients.http_client import get_info
def fetch_weather(api_key, city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"appid": api_key, "q": city}
    return get_info(url, params=params)