from flask import Flask, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .datacache import DataCache
from .weatherdata import WeatherAPIError, get_week, get_tomorrow, get_today


class WeatherAppError(Exception):
    pass


app = Flask(__name__)
CORS(app)
dbcache = DataCache("localhost", 6688)

limiter = Limiter(
    get_remote_address,  # Use the client's IP address as the key for rate limiting
    app=app,
    default_limits=["200 per day", "50 per hour"],  # Global rate limits
)


@app.route("/weather-today")
def weather_today() -> str:
    if tmp_location := request.args.get("location"):
        tmp_response: str | None
        if not (tmp_response := dbcache.read_cache(tmp_location)):
            tmp_response = get_today(location=tmp_location)
            dbcache.set_cache(tmp_location, tmp_response)
        return tmp_response
    raise WeatherAPIError("not location data")


@app.route("/weather-tomorrow")
def weather_tomorrow() -> str:
    if tmp_location := request.args.get("location"):
        tmp_response: str | None
        if not (tmp_response := dbcache.read_cache(tmp_location)):
            tmp_response = get_tomorrow(location=tmp_location)
            dbcache.set_cache(tmp_location, tmp_response)
        return tmp_response
    raise WeatherAPIError("not location data")


@app.route("/weather-weeks")
def weather_weeks() -> str:
    if tmp_location := request.args.get("location"):
        tmp_response: str | None
        if not (tmp_response := dbcache.read_cache(tmp_location)):
            tmp_response = get_week(location=tmp_location)
            dbcache.set_cache(tmp_location, tmp_response)
        return tmp_response
    raise WeatherAPIError("not location data")


@app.route("/ping")
@limiter.exempt
def ping():
    return "pong"


if "__main__" == __name__:
    app.run()
