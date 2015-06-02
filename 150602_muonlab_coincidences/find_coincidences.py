import tables

from sapphire.clusters import HiSPARCStations
from sapphire.analysis.coincidences import CoincidencesESD


STATIONS = [501, 510, 99]
EVENTDATA_PATH = '/Users/arne/Datastore/muonlab_test.h5'


def analyse_coincidences(data):
    """Find and store coincidences"""

    station_groups = ['/station_%d' % number for number in STATIONS]
    cluster = get_cluster()

    coin = CoincidencesESD(data, '/coincidences', station_groups)
    coin.search_coincidences(window=2000)
    coin.store_coincidences(cluster)


def get_cluster():
    """Get latest position from API"""

    return HiSPARCStations(STATIONS)


if __name__ == '__main__':
    with tables.open_file(EVENTDATA_PATH, 'a') as data:
        analyse_coincidences(data)
