#!/usr/bin/env python3
import json
import re
import uuid
from datetime import datetime, timedelta
from time import time

import pyexcel
import pytz
import vobject
from dateutil.parser import parse
from dateutil.rrule import rrule, rruleset, WEEKLY


INPUT_FILENAME = 'timetable-example.xls'
OUTPUT_FILENAME = 'timetable-example.ics'

LOCATION_REGEX = re.compile(r'(?P<campus>\w+)_(?P<street_number>\d+)(?P<street_code>\w+)/(?P<room>\w+)')
DURATION_REGEX = re.compile(r'([\d.]+) hrs?')

CLAYTON_STREET_NAMES = {
    'All': 'Alliance Lane',
    'Anc': 'Ancora Imparo Way',
    'Chn': 'Chancellors Walk',
    'Col': 'College Walk',
    'Exh': 'Exhibition Walk',
    'FGR': 'Ferntree Gully Road',
    'Inn': 'Innovation Walk',
    'Rnf': 'Rainforest Walk',
    'Res': 'Research Way',
    'Sce': 'Scenic Boulevard',
}

DEFAULT_TIMEZONE = pytz.timezone('Australia/Melbourne')


def get_pretty_location(location):
    if location.startswith('CL'):
        loc = LOCATION_REGEX.match(location).groupdict()
        street_name = CLAYTON_STREET_NAMES.get(loc.get('street_code', ''))

        return 'Room {room}, {street_number} {street_name}, Monash University Clayton Campus'.format(
            room=loc.get('room'),
            street_number=loc.get('street_number'),
            street_name=street_name,
        )

    return location


def parse_date(value):
    value += '/{year}'.format(year=datetime.now().year)
    return datetime.strptime(value, '%d/%m/%Y')


def parse_dates(dates, event_time, duration):
    date_ranges = []
    start_hour, start_minute = map(int, event_time.split(':'))

    raw_date_ranges = [date_range.strip() for date_range in dates.split(',')]
    for raw_date_range in raw_date_ranges:
        try:
            start_date, finish_date = raw_date_range.split('-')
        except ValueError:
            start_date = finish_date = raw_date_range.split('-')[0]

        date_ranges.append([
            parse_date(start_date).replace(hour=start_hour, minute=start_minute),
            parse_date(finish_date).replace(hour=start_hour, minute=start_minute),
        ])

    return date_ranges


def dates_between_dates(start_date, end_date, step=7, inclusive=False):
    dates = []
    delta = end_date - start_date

    # Adjust the offsets depending on whether or not
    # the result should be inclusive of the provided dates.
    start = 0 if inclusive else step
    offset = 1 if inclusive else 0

    for i in range(start, delta.days + offset, step):
        dates.append(start_date + timedelta(days=i))
    return dates


def build_event(record):
    date_ranges = parse_dates(record['Dates'], record['Time'], record['Duration'])
    excluded_dates = []

    duration = timedelta(hours=float(DURATION_REGEX.match(record['Duration']).group(1)))
    event_start = date_ranges[0][0]
    event_end = event_start + duration
    subject = record['Subject Code'].split('_')[0]

    for i, date_range in enumerate(date_ranges):
        if (i + 1) < len(date_ranges):
            previous_date = date_range[1]
            next_date = date_ranges[i + 1][0]
            excluded_dates.extend(dates_between_dates(previous_date, next_date))

    return {
        'event_start': DEFAULT_TIMEZONE.localize(event_start),
        'event_end': DEFAULT_TIMEZONE.localize(event_end),
        'day_index': parse(record['Day']).weekday(),
        'until': DEFAULT_TIMEZONE.localize(date_ranges[-1][-1]),
        'excludes': map(DEFAULT_TIMEZONE.localize, excluded_dates),
        'location': get_pretty_location(record['Location']),
        'title': '{subject} {group}'.format(subject=subject, group=record['Group']),
        'description': '{description}\n\nStaff: {staff}'.format(
            description=record['Description'],
            staff=record['Staff']
        )
    }


def filter_row(row_index, row):
    result = [element for element in row if element != '']
    return len(result) == 0


def main():
    sheet = pyexcel.get_sheet(file_name=INPUT_FILENAME, name_columns_by_row=1)
    del sheet.row[filter_row]  # Delete empty rows
    records = sheet.to_records()

    cal = vobject.iCalendar()
    for record in records:
        event = build_event(record)
        vevent = cal.add('vevent')
        vevent.add('uid').value = str(uuid.uuid4()).upper()
        vevent.add('summary').value = event['title']
        vevent.add('description').value = event['description']
        vevent.add('location').value = event['location']
        vevent.add('dtstart').value = event['event_start']
        vevent.add('dtend').value = event['event_end']

        ruleset = rruleset()
        ruleset.rrule(
            rrule(WEEKLY, byweekday=event['day_index'], until=event['until'])
        )

        for exdate in event['excludes']:
            ruleset.exdate(exdate)

        vevent.rruleset = ruleset

    with open(OUTPUT_FILENAME, 'w') as output:
        cal.serialize(output)


if __name__ == '__main__':
    t0 = time()
    main()
    t1 = time()
    print('{:0f} ms'.format((t1 - t0) * 1000))
