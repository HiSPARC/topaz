from datetime import date
import os

from numpy import (sum, sin, linspace, random, searchsorted, split, nan, array,
                   empty, column_stack)
import tables

from artist import Plot, MultiPlot

from sapphire.transformations.clock import datetime_to_gps
from sapphire.utils import pbar

from download_dataset import STATIONS, START, END

from determine_statistics import get_all_stats, BINS


def filter_data_days(statistics):
    """Remove days of data not satisfying requirements"""

    # A rate of 0.6 Hz is expected, it may be lower because a single detector
    # is bad, then 0.4 Hz is more reasonable. High event rates can also
    # indicate problems, such as light leaks.
    keep_slice = ((0.3 < statistics['event_rate']) &
                  (statistics['event_rate'] < 1.0))[0]
    # It seems 0.3% failure is to be expected for normal operation with filter.
    # Put cut on 1.0%
    keep_slice &= (statistics['t_trigger'] < 1.0)[0]
    # High failure rate indicates no data or bad calibration. Some events with
    # bad baseline, and thus bad n# are to be expected. Bad calibration causing
    # failure of MPV fit fails an entire day.
    # Perhaps cut per detector? (make entire days nan?)
    keep_slice &= sum(statistics['n1n2n3n4'] < 1.0, axis=0) == 4
    # MPV values are typically around 3000, drifting between 2000 and 4000.
    # Cut on 5000.
    keep_slice &= sum(statistics['mpv'] < 5000, axis=0) == 4

    return keep_slice


def filter_data_events():
    """Look for individual events to filter"""

    # Remove events that would not have triggered after accouting for MPV
    # The trigger shouls actually trigger on number of particles, not an
    # incorrectly calibrated pulseheight.
    low = 0.3
    high = 0.6

    n_high = sum(events['n%d' % (id + 1)] > high for id in range(4))
    n_low = sum(events['n%d' % (id + 1)] > low for id in range(4))
    keep_events = (n_high > 2) | (n_low > 3)

    return keep_events


def copy_selection(statistics):
    with tables.open_file(DATA_PATH) as source:
        with tables.open_file(FILTERED_PATH, 'w') as target:
            source
            target


if __name__ == "__main__":
    statistics = get_all_stats()
    keep_slices = filter_event_rate(statistics)
