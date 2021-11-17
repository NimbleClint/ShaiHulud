"""OpenWeatherMap widget for QTile"""

import requests

from libqtile import pangocffi
from libqtile.log_utils import logger
from libqtile.widget import base

__author__ = "Simon Kennedy <sffjunkie+code@mail.com>"
__version__ = "0.2"

ICON_FONT = "Weather Icons"

ICONS = {
    "Weather Icons": {    # https://github.com/erikflowers/weather-icons
        "01d": "\uF00D",  # Clear sky
        "01n": "\uF02E",
        "02d": "\uF002",  # Few clouds
        "02n": "\uF086",
        "03d": "\uF041",  # Scattered Clouds
        "03n": "\uF041",
        "04d": "\uF013",  # Broken clouds
        "04n": "\uF013",
        "09d": "\uF009",  # Shower Rain
        "09n": "\uF037",
        "10d": "\uF008",  # Rain
        "10n": "\uF036",
        "11d": "\uF010",  # Thunderstorm
        "11n": "\uF03B",
        "13d": "\uF00A",  # Snow
        "13n": "\uF038",
        "50d": "\uF003",  # Mist
        "50n": "\uF04A",
        "sleetd": "\uF0B2",
        "sleetn": "\uF0B3",
    },
    "Material Design Icons": {
        "01d": "\U000F0599",  # Clear sky
        "01n": "\U000F0594",
        "02d": "\U000F0595",  # Few clouds
        "02n": "\U000F0F31",
        "03d": "\U000F0595",  # Scattered Clouds
        "03n": "\U000F0F31",
        "04d": "\U000F0590",  # Broken clouds
        "04n": "\U000F0F31",
        "09d": "\U000F0F33",  # Shower Rain
        "09n": "\U000F0F33",
        "10d": "\U000F0597",  # Rain
        "10n": "\U000F0597",
        "11d": "\U000F0596",  # Thunderstorm
        "11n": "\U000F0596",
        "13d": "\U000F0598",  # Snow
        "13n": "\U000F0598",
        "50d": "\U000F0591",  # Mist
        "50n": "\U000F0591",
        "sleetd": "\U000F0596",
        "sleetn": "\U000F0596",
    },
}

CONDITION_CODES = {
    200: ("thunderstorm with light rain", "11d", "11n"),
    201: ("thunderstorm with rain", "11d", "11n"),
    202: ("thunderstorm with heavy rain", "11d", "11n"),
    210: ("light thunderstorm", "11d", "11n"),
    211: ("thunderstorm", "11d", "11n"),
    212: ("heavy thunderstorm", "11d", "11n"),
    221: ("ragged thunderstorm", "11d", "11n"),
    230: ("thunderstorm with light drizzle", "11d", "11n"),
    231: ("thunderstorm with drizzle", "11d", "11n"),
    232: ("thunderstorm with heavy drizzle", "11d", "11n"),
    300: ("light intensity drizzle", "09d", "09n"),
    301: ("drizzle", "09d", "09n"),
    302: ("heavy intensity drizzle", "09d", "09n"),
    310: ("light intensity drizzle rain", "09d", "09n"),
    311: ("drizzle rain", "09d", "09n"),
    312: ("heavy intensity drizzle rain", "09d", "09n"),
    313: ("shower rain and drizzle", "09d", "09n"),
    314: ("heavy shower rain and drizle", "09d", "09n"),
    321: ("shower drizzle", "09d", "09n"),
    500: ("light rain", "10d", "10n"),
    501: ("moderatelight rain", "10d", "10n"),
    502: ("heavy intensity rain", "10d", "10n"),
    503: ("very heavy rain", "10d", "10n"),
    504: ("extreme rain", "10d", "10n"),
    511: ("freezing rain", "13d", "13n"),
    520: ("light intensity shower rain", "09d", "09n"),
    521: ("shower rain", "09d", "09n"),
    522: ("heavy intensity shower rain", "09d", "09n"),
    531: ("ragged shower rain", "09d", "09n"),
    600: ("light snow", "13d", "13n"),
    601: ("snow", "13d", "13n"),
    602: ("heavy snow", "13d", "13n"),
    611: ("sleet", "sleetd", "sleetn"),
    612: ("light shower sleet", "13d", "13n"),
    613: ("shower sleet", "13d", "13n"),
    615: ("light rain and snow", "13d", "13n"),
    616: ("rain and snow", "13d", "13n"),
    620: ("light shower snow", "13d", "13n"),
    621: ("shower snow", "13d", "13n"),
    622: ("heavy shower snow", "13d", "13n"),
    701: ("mist", "50d", "50n"),
    711: ("smoke", "50d", "50n"),
    721: ("haze", "50d", "50n"),
    731: ("sand / dust swirls", "50d", "50n"),
    741: ("fog", "50d", "50n"),
    751: ("sand", "50d", "50n"),
    761: ("dust", "50d", "50n"),
    762: ("volcanic ash", "50d", "50n"),
    771: ("squalls", "50d", "50n"),
    781: ("tornado", "50d", "50n"),
    800: ("clear sky", "01d", "01n"),
    801: ("few clouds", "02d", "02n"),
    802: ("scattered clouds", "03d", "03n"),
    803: ("broken clouds", "04d", "04d"),
    804: ("overcast clouds", "04d", "04d"),
}

# Handle the change of widget base class in the Qtile project
try:
    BaseClass = base.ThreadPoolText
    NewWidgetBase = True
except AttributeError:
    BaseClass = base.ThreadedPollText # pylint: disable=no-member
    NewWidgetBase = False

class OpenWeatherMap(BaseClass):
    """OpenWeatherMap widget for QTile"""

    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ("api_key", "", "API Key for OpenWeatherMap data"),
        ("icon_font", None, "Font to use for weather icons"),
        ("format", "{temp:.1f}{temp_units} {icon}", "Format string",),
        ("update_interval", 3600, "Update interval in seconds between look ups"),
        ("latitude", 51.4934, "Latitude to look up weather data for"),
        ("longitude", 0.0098, "Longitude to look up weather data for"),
        ("units", "metric", "Temperature units to use"),
    ]

    def __init__(self, **config):
        if NewWidgetBase:
            super().__init__("", **config)
        else:
            super().__init__(**config)

        self.add_defaults(OpenWeatherMap.defaults)
        if not self.api_key:
            logger.exception(
                "OpenWeatherMap: An API key is required. Pass as the `api_key` parameter"
            )
        self.url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.latitude}&lon={self.longitude}&appid={self.api_key}&units={self.units}"
        if not self.icon_font: # pylint: disable=access-member-before-definition # icon_font created by add_defaults
            self.icon_font = ICON_FONT
        self.markup = True

    def poll(self):
        resp = requests.get(self.url)
        self.status = resp.status_code
        if resp.status_code == 200:
            _lookup = lambda group, key: group[key] if key in group else ""
            data = resp.json()
            owm_icon = _lookup(data["weather"][0], "icon")
            day = owm_icon[-1] == "d"

            owm_condition = _lookup(data["weather"][0], "id")
            if owm_condition in CONDITION_CODES:
                condition = CONDITION_CODES[owm_condition][0].capitalize()
                if day:
                    icon_id = CONDITION_CODES[owm_condition][1]
                else:
                    icon_id = CONDITION_CODES[owm_condition][2]
            else:
                condition = "Unknown"
                logger.warning(
                    f"OpenWeatherMap: Unknown condition {owm_condition} received"
                )
                if day:
                    icon_id = "01d"
                else:
                    icon_id = "01n"

            temp_units = {"metric": "°C", "imperial": "°F", "standard": "°K"}[
                self.units
            ]
            self.format = self.format.replace("{icon}", '<span face="{icon_font}">{icon}</span>')
            info = {
                "icon": ICONS[self.icon_font][icon_id],
                "icon_font": self.icon_font,
                "condition": condition,
                "temp_units": temp_units,
                "temp": _lookup(data["main"], "temp"),
                "temp_min": _lookup(data["main"], "temp_min"),
                "temp_max": _lookup(data["main"], "temp_max"),
                "temp_feels_like": _lookup(data["main"], "feels_like"),
                "pressure": _lookup(data["main"], "pressure"),
                "humidity": _lookup(data["main"], "humidity"),
            }

            return self.format.format(**info)
        else:
            return f"OpenWeatherMap Error {resp.status_code}"
