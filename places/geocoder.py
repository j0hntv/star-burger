from geopy.distance import distance
import requests

from .models import Place


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_place_coordinates(apikey, address, saved_places):
    place = saved_places.get(address)

    if not place:
        place_fields = {'address': address}
        coordinates = fetch_coordinates(apikey, address)
        if coordinates:
            place_fields['lat'], place_fields['lon'] = coordinates

        place = Place.objects.create(**place_fields)

    return place['lat'], place['lon']


def calculate_distance(apikey, address_1, address_2, saved_places):
    lat_1, lon_1 = get_place_coordinates(apikey, address_1, saved_places)
    lat_2, lon_2  = get_place_coordinates(apikey, address_2, saved_places)

    if all((lat_1, lon_1, lat_2, lon_2)):
        return distance((lat_1, lon_1), (lat_2, lon_2)).km
