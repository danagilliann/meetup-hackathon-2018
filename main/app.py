from datetime import datetime

import requests
import secrets
from main.classes.availability import Availability


def get_results():
    api_key = secrets.api_key
    oauth_key = secrets.oauth_key
    oauth_secret = secrets.oauth_secret
    username = secrets.username
    password = secrets.password

    market_id = "dac1820e-5dae-4c0c-9be8-8916e7aa724a"
    req_url = "https://api.meetup.com/maw/bookable_spaces?key=" + api_key + "&market_id=" + market_id

    results = requests.get(req_url)

    return results.json()


def iso_to_datetime(iso=""):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')


def is_conflicting(reservation_start_time, reservation_end_time, req_start_time, req_end_time):
    if int(reservation_start_time.year) == int(req_start_time.year) and \
            int(reservation_start_time.month) == int(req_start_time.month) and \
            int(reservation_start_time.day) == int(req_start_time.day) and \
            (int(reservation_start_time) < int(req_start_time) < int(reservation_end_time) or \
            int(reservation_start_time) < int(req_end_time) < int(reservation_end_time)):
        return True
    return False


def find_availability(results, starttime, endtime):
    req_start_time = iso_to_datetime(starttime)
    req_end_time = iso_to_datetime(endtime)
    availability_list = []

    data = results.data

    for location in data:
        rooms = location.rooms.data

        for room in rooms:
            reservations = room.reservations

            for reservation in reservations:
                reservation_start_time = iso_to_datetime(reservation.start)
                reservation_end_time = iso_to_datetime(reservation.finish)

                if not is_conflicting(reservation_start_time, reservation_end_time, req_start_time, req_end_time):
                    availability_info = {}

                    availability_info["location_id"] = location.id
                    availability_info["room_id"] = room.id

                    availability_list.append(availability_info)


if __name__ == '__main__':
    results = get_results()
