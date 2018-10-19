from builtins import int
from datetime import datetime

import requests
import secrets
import pprint
from main.classes.availability import Availability


def get_results(market_id):
    api_key = secrets.api_key
    oauth_key = secrets.oauth_key
    oauth_secret = secrets.oauth_secret
    username = secrets.username
    password = secrets.password

    req_url = "https://api.meetup.com/maw/bookable_spaces?key=" + api_key + "&market_id=" + market_id

    results = requests.get(req_url)

    return results.json()


def iso_to_datetime(iso=""):
    return datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.000Z')


def is_conflicting(reservation_start_time, reservation_end_time, req_start_time, req_end_time):
    pp = pprint.PrettyPrinter(indent=2)

    reservation_start_time_hourminute = int(reservation_start_time.hour + reservation_start_time.minute)
    reservation_end_time_hourminute = int(reservation_end_time.hour + reservation_end_time.minute)
    req_start_time_hourminute = int(req_start_time.hour + req_end_time.minute)
    req_end_time_hourminute = int(req_end_time.hour + req_end_time.minute)

    if int(reservation_start_time.year) == int(req_start_time.year) and \
            int(reservation_start_time.month) == int(req_start_time.month) and \
            int(reservation_start_time.day) == int(req_start_time.day) and \
            (reservation_start_time_hourminute < req_start_time_hourminute < reservation_start_time_hourminute or \
             reservation_start_time_hourminute < req_end_time_hourminute < reservation_end_time_hourminute):
        return True
    return False


def find_availability(results, starttime, endtime):
    pp = pprint.PrettyPrinter(indent=2)

    req_start_time = iso_to_datetime(starttime)
    req_end_time = iso_to_datetime(endtime)
    availability_list = []

    data = results.get('data')

    for location in data:
        rooms = location.get('attributes').get('rooms').get('data')
        for room in rooms:
            reservations = room.get('attributes').get('reservations')

            for reservation in reservations:
                reservation_start_time = iso_to_datetime(reservation.get('start'))
                reservation_end_time = iso_to_datetime(reservation.get('finish'))

                if is_conflicting(reservation_start_time, reservation_end_time, req_start_time, req_end_time):
                    continue

            availability_info = {"location_id": location.get('id'), "room_id": room.get('id')}
            availability_list.append(availability_info)

    pp.pprint(availability_list)


if __name__ == '__main__':
    starttime = "2018-11-07T17:30:00.000Z"
    endtime = "2018-11-07T19:00:00.000Z"
    market_id = "dac1820e-5dae-4c0c-9be8-8916e7aa724a"

    results = get_results(market_id)
    find_availability(results, starttime, endtime)
