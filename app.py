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
from flask import Flask

from utils import dates_between_dates, filter_row, get_pretty_location, parse_dates


app = Flask(__name__)

INPUT_FILENAME = 'timetable-example.xls'
OUTPUT_FILENAME = 'timetable-example.ics'

DURATION_REGEX = re.compile(r'([\d.]+) hrs?')


DEFAULT_TIMEZONE = pytz.timezone('Australia/Melbourne')


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


@app.route('/')
def home():
    t0 = time()

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

    t1 = time()
    return '{:0f} ms'.format((t1 - t0) * 1000)


if __name__ == '__main__':
    app.run()
