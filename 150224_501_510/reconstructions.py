import tables

from sapphire import HiSPARCStations, ReconstructESDEvents

STATIONS = [501, 510]
COINDATA_PATH = '/Users/arne/Datastore/501_510/c_501_510_141101_150201.h5'
# COINDATA_PATH = '/Users/arne/Datastore/501_510/c_501_510_150120_150201.h5'


def reconstruct_events(data):
    """Reconstruct and store the data

    Do not let it determine offsets, because events are filtered for
    coincidences. However, in this case it should make little
    difference, because the stations are ontop of each other, so hardly
    any azimuthal preference.

    """
    cluster = get_cluster()

    for number in STATIONS:
        station = cluster.get_station(number)
        station_group = '/hisparc/cluster_amsterdam/station_%d' % number
        rec_events = ReconstructESDEvents(data, station_group, station, overwrite=True, progress=True)
        rec_events.offsets = offset(number)
        rec_events.store_offsets()
        rec_events.reconstruct_directions()
        rec_events.reconstruct_cores()
        rec_events.prepare_output()
        rec_events.store_reconstructions()


def offset(station):
    """Offsets determined from event data (before filtering coincidences)"""

    if station == 501:
        return [-1.064884, 0.0, 6.217017, 4.851398]
    elif station == 510:
        return [9.416971, 0.0, 9.298256, 8.447724]


def get_cluster():
    """Get latest position from API"""

    return HiSPARCStations(STATIONS)


if __name__ == '__main__':
    with tables.open_file(COINDATA_PATH, 'a') as data:
        reconstruct_events(data)
