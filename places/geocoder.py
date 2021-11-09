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
    print(address)
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_coordinates(apikey, address):
    place = Place.objects.filter(address=address).first()

    if not place:
        place = Place(address=address)
        place.lat, place.lon = fetch_coordinates(apikey, address)
        place.save()

    return place.lat, place.lon


def calculate_distance(apikey, address_1, address_2):
    coordinates_1 = get_coordinates(apikey, address_1)
    coordinates_2 = get_coordinates(apikey, address_2)
    return distance(coordinates_1, coordinates_2).km
