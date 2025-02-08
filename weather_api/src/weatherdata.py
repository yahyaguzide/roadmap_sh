from os import getenv
from datetime import datetime, timedelta
import requests


_URL = r"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date1}/{date2}?key={API_TOKEN}"


class WeatherAPIError(Exception):
    pass


def _get_data(location: str, date1: str, date2: str) -> dict[str, str]:
    if api_token := getenv("API_TOKEN"):
        response = requests.get(
            _URL.format(
                location=location, date1=date1, date2=date2, API_TOKEN=api_token
            )
        )

        if response.status_code != 200:
            raise WeatherAPIError("Coudn't read data from endpoint")
        return response.json()
    raise WeatherAPIError("No api key found, please set API_TOKEN")


def get_today(location: str) -> str:
    today = str(datetime.today())
    return str(_get_data(location=location, date1=today, date2=today))


def get_tomorrow(location: str) -> str:
    date1 = str(datetime.today())
    date2 = str(datetime.today() + timedelta(days=1))
    return str(_get_data(location=location, date1=date1, date2=date2))


def get_week(location: str) -> str:
    date1 = str(datetime.today())
    date2 = str(datetime.today() + timedelta(days=5))
    return str(_get_data(location=location, date1=date1, date2=date2))
