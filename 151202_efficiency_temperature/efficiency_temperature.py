import os

from datetime import datetime

import tables

from numpy import arange, histogram, interp

from sapphire import FindMostProbableValueInSpectrum, download_data

DATA_PATH = '/Users/arne/Datastore/efficiency_temperature/data.h5'


def get_weather_data_dataset():
    if os.path.exists(DATA_PATH):
        print('Datafile already exists, skipping download')
        return

    with tables.open_file(DATA_PATH, 'a') as data:
        for station in [501]:  # , 502, 503, 504, 505, 506, 508, 509, 510]:
            for data_type in ['weather', 'events']:
                download_data(
                    data, '/s%d' % station, station, datetime(2015, 10, 1), datetime(2015, 10, 15), type=data_type
                )


def get_value_at_timestamp(event_ts, weather_ts, weather_quantity):
    return interp(event_ts, weather_ts, weather_quantity)


def fit_mpv(pulseintegrals):
    bins = arange(0, 100, 0)
    counts, bins = histogram(pulseintegrals)
    find_mpv = FindMostProbableValueInSpectrum(counts, bins)


# interpolate (or bisect?) to get temperature and solar radiation at time
# of the events.


if __name__ == "__main__":
    get_weather_data_dataset()
