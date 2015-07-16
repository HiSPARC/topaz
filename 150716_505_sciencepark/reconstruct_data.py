import tables
from artist import Plot
import numpy as np

from sapphire import (CoincidenceQuery, ReconstructESDEvents,
                      ReconstructESDCoincidences)
from sapphire.utils import angle_between

DATA_PATH = '/Users/arne/Datastore/esd_coincidences/coincidences_n7_100101_140801.h5'


def reconstruct_data(data):

#     rec = ReconstructESDCoincidences(data, overwrite=True)
#     rec.reconstruct_and_store()

    station_path = '/hisparc/cluster_amsterdam/station_505'
    rec = ReconstructESDEvents(data, station_path, 505, overwrite=True)
    rec.prepare_output()
    rec.offsets = [-0.53,0.0,1.64,-2.55]
    rec.store_offsets()
    rec.reconstruct_directions()
    rec.store_reconstructions()


def analyse_reconstructions(data):
    cq = CoincidenceQuery(data)
    c_ids = data.root.coincidences.coincidences.read_where('s505 & (timestamp < 1366761600)', field='id')
    c_recs = cq.reconstructions.read_coordinates(c_ids)

    s_ids = data.root.hisparc.cluster_amsterdam.station_505.events.get_where_list('timestamp < 1366761600')
    s_recs = data.root.hisparc.cluster_amsterdam.station_505.reconstructions.read_coordinates(s_ids)

    assert len(c_recs) == len(s_recs)

    zenc = c_recs['zenith']
    azic = c_recs['azimuth']

    zens = s_recs['zenith']
    azis = s_recs['azimuth']

    high_zenith = (zenc > .2) & (zens > .2)

    for minn in [1, 2, 4, 8, 16]:
        filter = (s_recs['min_n'] > minn)

        length = len(azis.compress(high_zenith & filter))
        shifts501 = np.random.normal(0, .06, length)
        azicounts, x, y = np.histogram2d(azis.compress(high_zenith & filter) + shifts501,
                                         azic.compress(high_zenith & filter),
                                         bins=np.linspace(-np.pi, np.pi, 73))
        plota = Plot()
        plota.histogram2d(azicounts, np.degrees(x), np.degrees(y), type='reverse_bw', bitmap=True)
#         plota.set_title('Reconstructed azimuths for events in coincidence (zenith gt .2 rad)')
        plota.set_xlabel(r'$\phi_{505}$ [\si{\degree}]')
        plota.set_ylabel(r'$\phi_{Science Park}$ [\si{\degree}]')
        plota.set_xticks([-180, -90, 0, 90, 180])
        plota.set_yticks([-180, -90, 0, 90, 180])
        plota.save_as_pdf('azimuth_505_spa_minn%d' % minn)


if __name__ == '__main__':
    with tables.open_file(DATA_PATH, 'a') as data:
        reconstruct_data(data)
    with tables.open_file(DATA_PATH, 'r') as data:
        analyse_reconstructions(data)
