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


def parse_time(hour, minute):
    return int(hour + minute)


def get_opening_hours(meetupable_data):
    pp = pprint.PrettyPrinter(indent=2)

    opening_hours = {}

    weekly_schedule = meetupable_data.get('weekly_schedule')

    if weekly_schedule.get('monday'):
        opening_hours[0] = weekly_schedule.get('monday_times')
    elif weekly_schedule.get('tuesday'):
        opening_hours[1] = weekly_schedule.get('tuesday_times')
    elif weekly_schedule.get('wednesday'):
        opening_hours[2] = weekly_schedule.get('wednesday_times')
    elif weekly_schedule.get('thursday'):
        opening_hours[3] = weekly_schedule.get('thursday_times')
    elif weekly_schedule.get('friday'):
        opening_hours[4] = weekly_schedule.get('friday_times')
    elif weekly_schedule.get('saturday'):
        opening_hours[5] = weekly_schedule.get('saturday_times')
    elif weekly_schedule.get('sunday'):
        opening_hours[6] = weekly_schedule.get('sunday_times')

    return opening_hours


def is_hour_minute_problematic(wework_start_time_hour_minute=0, wework_end_time_hour_minute=0,
                               req_start_time_hour_minute=0, req_end_time_hour_minute=0):
    if (wework_start_time_hour_minute < req_start_time_hour_minute < wework_start_time_hour_minute or
            wework_start_time_hour_minute < req_end_time_hour_minute < wework_end_time_hour_minute):
        return False
    return True


def is_day_booked(wework_start_time_year=0, wework_start_time_month=0, wework_start_time_day=0,
                  req_start_time_year=0, req_start_time_month=0, req_start_time_day=0):
    return wework_start_time_year == req_start_time_year and \
           wework_start_time_month == req_start_time_month and \
           wework_start_time_day == req_start_time_day


def is_meetupable(opening_hours={}, req_start_time=datetime, req_end_time=datetime):
    req_start_day_of_the_week = req_start_time.weekday()
    req_end_day_of_the_week = req_end_time.weekday()

    if req_start_day_of_the_week != req_end_day_of_the_week:
        return False

    opening_times = opening_hours.get(req_start_day_of_the_week)

    if opening_times is not None:
        for times in opening_times:
            open_time = int(times.get('open_time').replace(":", ""))
            close_time = int(times.get('close_time').replace(":", ""))

            req_start_time_hour_minute = parse_time(req_start_time.hour, req_end_time.minute)
            req_end_time_hour_minute = parse_time(req_end_time.hour, req_end_time.minute)

            return is_hour_minute_problematic(open_time, close_time, req_start_time_hour_minute,
                                              req_end_time_hour_minute)


def is_conflicting(reservation_start_time=datetime, reservation_end_time=datetime, req_start_time=datetime,
                   req_end_time=datetime):
    pp = pprint.PrettyPrinter(indent=2)

    reservation_start_time_hour_minute = parse_time(reservation_start_time.hour, reservation_start_time.minute)
    reservation_end_time_hour_minute = parse_time(reservation_end_time.hour, reservation_end_time.minute)
    req_start_time_hour_minute = parse_time(req_start_time.hour, req_end_time.minute)
    req_end_time_hour_minute = parse_time(req_end_time.hour, req_end_time.minute)

    if is_day_booked(int(reservation_start_time.year), int(reservation_start_time.month), int(reservation_start_time.day),
                     int(req_start_time.year), int(req_start_time.month), int(req_start_time.day)) and \
            not is_hour_minute_problematic(reservation_start_time_hour_minute, reservation_end_time_hour_minute,
                                           req_start_time_hour_minute, req_end_time_hour_minute):
        return True
    return False


def find_availability(results={}, start_time=datetime, end_time=datetime):
    pp = pprint.PrettyPrinter(indent=2)

    req_start_time = iso_to_datetime(start_time)
    req_end_time = iso_to_datetime(end_time)
    availability_list = []

    data = results.get('data')

    for location in data:
        rooms = location.get('attributes').get('rooms').get('data')
        for room in rooms:
            reservations = room.get('attributes').get('reservations')

            opening_hours = get_opening_hours(room.get('attributes').get('meetupable'))

            if is_meetupable(opening_hours, req_start_time, req_end_time):
                for reservation in reservations:
                    reservation_start_time = iso_to_datetime(reservation.get('start'))
                    reservation_end_time = iso_to_datetime(reservation.get('finish'))

                    if is_conflicting(reservation_start_time, reservation_end_time, req_start_time, req_end_time):
                        continue

            availability_info = {"location_id": location.get('id'), "room_id": room.get('id')}
            availability_list.append(availability_info)

    pp.pprint(availability_list)


if __name__ == '__main__':
    user_starttime = "2018-11-07T17:30:00.000Z"
    user_endtime = "2018-11-07T19:00:00.000Z"
    market_id = "dac1820e-5dae-4c0c-9be8-8916e7aa724a"

    api_results = get_results(market_id)
    find_availability(api_results, user_starttime, user_endtime)
