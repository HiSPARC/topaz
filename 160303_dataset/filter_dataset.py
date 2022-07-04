import tables

from numpy import ones_like, sum

from determine_statistics import get_all_stats


class DayFilter:

    """Remove days of data not satisfying requirements

    :param statistics: dictionry of data statistics from determine_statistics.

    """

    def __init__(self, statistics):
        self.stats = statistics

    def data_filter(self):
        """Get a filter to be used to keep good data

        :return: days to keep.

        """
        keep_slice = ones_like(self.stats['event_rate'], dtype=bool)
        keep_slice &= self.filter_event_rate()
        keep_slice &= self.filter_trigger_time()
        keep_slice &= self.filter_particle_density()
        keep_slice &= self.filter_mpv()
        return keep_slice

    def filter_event_rate(self):
        """Filter event rate statistics

        A rate of 0.6 Hz is expected, it may be lower because a single detector
        is bad, then 0.4 Hz is more reasonable. High event rates can also
        indicate problems, such as light leaks.

        """
        return ((0.3 < self.stats['event_rate']) & (self.stats['event_rate'] < 1.0))[0]

    def filter_trigger_time(self):
        """Filter event rate statistics

        It seems 0.3% failure is to be expected for normal operation with filter.
        Put cut on 1.0%

        """
        return (self.stats['t_trigger'] < 1.0)[0]

    def filter_particle_density(self):
        """Filter event rate statistics

        High failure rate indicates no data or bad calibration. Some events with
        bad baseline, and thus bad n# are to be expected. Bad calibration causing
        failure of MPV fit fails an entire day.
        Perhaps cut per detector? (make entire days nan?)

        """
        return sum(self.stats['n1n2n3n4'] < 1.0, axis=0) == 4

    def filter_mpv(self):
        """Filter event rate statistics

        MPV values are typically around 3000, drifting between 2000 and 4000.
        Cut on 5000.

        """
        return sum(self.stats['mpv'] < 5000, axis=0) == 4

    def filter_configuration(self):
        """Filter event rate statistics

        MPV values are typically around 3000, drifting between 2000 and 4000.
        Cut on 5000.

        """
        return sum(self.stats['mpv'] < 5000, axis=0) == 4


class EventFilter:

    """Remove station events not satisfying requirements

    :param statistics: dictionary of data statistics from determine_statistics.

    """

    def __init__(self, events):
        self.events = events

    def data_filter(self):
        keep_filter = self.filter_offline_trigger()

    def filter_offline_trigger(self):
        """Look for individual events to filter"""

        # Remove events that would not have triggered after accouting for MPV
        # The trigger shouls actually trigger on number of particles, not an
        # incorrectly calibrated pulseheight.
        low = 0.3
        high = 0.6

        n_high = sum(self.events['n%d' % (id + 1)] > high for id in range(4))
        n_low = sum(self.events['n%d' % (id + 1)] > low for id in range(4))
        return (n_high > 2) | (n_low > 3)


def copy_selection(statistics):
    """Copy the selected events to a new tables

    WIP

    """
    with tables.open_file(DATA_PATH) as source:
        with tables.open_file(FILTERED_PATH, 'w') as target:
            source
            target


if __name__ == "__main__":
    statistics = get_all_stats()
    keep_slices = filter_event_rate(statistics)
