from builtins import int
from datetime import datetime

import requests
import secrets
import unittest
import app


class TestApp(unittest.TestCase):

    def test_get_opening_hours(self):
        meetupable_data = {
            'weekly_schedule': {
                'monday': True,
                'tuesday': False,
                'monday_times': [{
                    'open_time': '18:00',
                    'close_time': '21:00'
                }]
            }
        }

        opening_hours = {
            0: [{
                'open_time': '18:00',
                'close_time': '21:00'
            }]
        }

        self.assertEqual(app.get_opening_hours(meetupable_data), opening_hours)

    def test_is_hour_minute_intersecting(self):
        wework_start_time = 1830
        wework_end_time = 2030

        req_start_time_intersects = 1800
        req_end_time_intersects = 1900

        req_start_time_no_intersects = 1700
        req_end_time_no_intersects = 1730

        self.assertTrue(app.is_hour_minute_intersecting(wework_start_time,
                                                        wework_end_time,
                                                        req_start_time_intersects,
                                                        req_end_time_intersects))

        self.assertFalse(app.is_hour_minute_intersecting(wework_start_time,
                                                         wework_end_time,
                                                         req_start_time_no_intersects,
                                                         req_end_time_no_intersects))

    def test_is_same_day(self):
        self.assertTrue(app.is_same_day(2018, 11, 15, 2018, 11, 15))
        self.assertFalse(app.is_same_day(2018, 11, 15, 2018, 10, 15))

    def is_meetupable(self):
        opening_hours = {
            0: [{
                'open_time': '18:00',
                'close_time': '21:00'
            }]
        }

        meetupable_req_start_time = datetime(2018, 10, 15, 19, 00)
        meetupable_req_end_time = datetime(2018, 10, 15, 19, 30)

        not_meetupable_time_req_start_time = datetime(2018, 10, 15, 17, 00)
        not_meetupable_time_req_end_time = datetime(2018, 10, 15, 17, 30)

        not_meetupable_date_req_start_time = datetime(2018, 10, 12, 17, 00)
        not_meetupable_date_req_end_time = datetime(2018, 10, 12, 17, 30)

        not_meetupable_overnight_req_start_time = datetime(2018, 10, 11, 17, 00)
        not_meetupable_overnight_req_end_time = datetime(2018, 10, 12, 17, 30)

        self.assertTrue(app.is_meetupable(opening_hours, meetupable_req_start_time, meetupable_req_end_time))
        self.assertFalse(app.is_meetupable(opening_hours, not_meetupable_date_req_start_time,
                                           not_meetupable_date_req_end_time))
        self.assertFalse(app.is_meetupable(opening_hours, not_meetupable_time_req_start_time,
                                           not_meetupable_time_req_end_time))
        self.assertFalse(app.is_meetupable(opening_hours, not_meetupable_overnight_req_start_time,
                                           not_meetupable_overnight_req_end_time))

    def test_is_conflicting(self):
        reservation_start_time = datetime(2018, 10, 15, 18, 30)
        reservation_end_time = datetime(2018, 10, 15, 19, 30)

        conflict_req_start_time = datetime(2018, 10, 15, 18, 00)
        conflict_req_end_time = datetime(2018, 10, 15, 19, 30)

        no_conflict_req_start_time = datetime(2018, 10, 15, 20, 00)
        no_conflict_req_end_time = datetime(2018, 10, 15, 20, 30)

        reservation_start_time_parse = app.parse_time(reservation_start_time.hour,
                                                      reservation_start_time.minute)
        reservation_end_time_parse = app.parse_time(reservation_end_time.hour,
                                                    reservation_end_time.minute)

        conflict_req_start_time_parse = app.parse_time(conflict_req_start_time.hour,
                                                       conflict_req_start_time.minute)
        conflict_req_end_time_parse = app.parse_time(conflict_req_end_time.hour,
                                                     conflict_req_end_time.minute)

        no_conflict_req_start_time_parse = app.parse_time(no_conflict_req_start_time.hour,
                                                          no_conflict_req_start_time.minute)
        no_conflict_req_end_time_parse = app.parse_time(no_conflict_req_end_time.hour,
                                                        no_conflict_req_end_time.minute)

        self.assertEqual(no_conflict_req_start_time_parse, 2000)
        self.assertEqual(no_conflict_req_end_time_parse, 2030)

        self.assertEqual(conflict_req_start_time_parse, 1800)
        self.assertEqual(conflict_req_end_time_parse, 1930)

        self.assertEqual(reservation_start_time_parse, 1830)
        self.assertEqual(reservation_end_time_parse, 1930)

        self.assertTrue(app.is_hour_minute_intersecting(reservation_start_time_parse, reservation_end_time_parse,
                                                        conflict_req_start_time_parse, conflict_req_end_time_parse))

        self.assertTrue(app.is_conflicting(reservation_start_time, reservation_end_time,
                                           conflict_req_start_time, conflict_req_end_time))
        self.assertFalse(app.is_conflicting(reservation_start_time, reservation_end_time,
                                            no_conflict_req_start_time, no_conflict_req_end_time))

    def test_parse_time(self):
        self.assertEqual(app.parse_time('15', '30'), 1530)


if __name__ == '__main__':
    unittest.main()
