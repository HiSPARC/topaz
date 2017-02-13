import tables
from artist import Plot
import numpy as np

from sapphire import (CoincidenceQuery, ReconstructESDEvents,
                      ReconstructESDCoincidences)
from sapphire.utils import angle_between

DATA_PATH = '/Users/arne/Datastore/esd_coincidences/coincidences_n7_100101_140801.h5'


def reconstruct_data(data):

    rec = ReconstructESDCoincidences(data, overwrite=True)
    rec.reconstruct_and_store()

    station_path = '/hisparc/cluster_amsterdam/station_501'
    rec = ReconstructESDEvents(data, station_path, 501, overwrite=True)
    # rec.reconstruct_and_store()
    rec.prepare_output()
    rec.offsets = [-1.10338, 0.0000, 5.35711, 3.1686]
    rec.store_offsets()
    rec.reconstruct_directions()
    rec.reconstruct_cores()
    rec.store_reconstructions()


def analyse_reconstructions(data):
    cq = CoincidenceQuery(data)
    c_ids = data.root.coincidences.coincidences.read_where('s501', field='id')
    c_recs = cq.reconstructions.read_coordinates(c_ids)

    s_recs = data.root.hisparc.cluster_amsterdam.station_501.reconstructions

    zenc = c_recs['zenith']
    azic = c_recs['azimuth']

    zens = s_recs.col('zenith')
    azis = s_recs.col('azimuth')

    high_zenith = (zenc > .2) & (zens > .2)

    for minn in [1, 2, 4, 8, 16]:
        filter = (s_recs.col('min_n') > minn)

        length = len(azis.compress(high_zenith & filter))
        shifts501 = np.random.normal(0, .06, length)
        azicounts, x, y = np.histogram2d(azis.compress(high_zenith & filter) + shifts501,
                                         azic.compress(high_zenith & filter),
                                         bins=np.linspace(-np.pi, np.pi, 73))
        plota = Plot()
        plota.histogram2d(azicounts, np.degrees(x), np.degrees(y), type='reverse_bw', bitmap=True)
        # plota.set_title('Reconstructed azimuths for events in coincidence (zenith gt .2 rad)')
        plota.set_xlabel(r'$\phi_{501}$ [\si{\degree}]')
        plota.set_ylabel(r'$\phi_{Science Park}$ [\si{\degree}]')
        plota.set_xticks([-180, -90, 0, 90, 180])
        plota.set_yticks([-180, -90, 0, 90, 180])
        plota.save_as_pdf('azimuth_501_spa_minn%d' % minn)

        length = sum(filter)
        shifts501 = np.random.normal(0, .04, length)

        zencounts, x, y = np.histogram2d(zens.compress(filter) + shifts501,
                                         zenc.compress(filter),
                                         bins=np.linspace(0, np.pi / 3., 41))
        plotz = Plot()
        plotz.histogram2d(zencounts, np.degrees(x), np.degrees(y), type='reverse_bw', bitmap=True)
        # plotz.set_title('Reconstructed zeniths for station events in coincidence')
        plotz.set_xlabel(r'$\theta_{501}$ [\si{\degree}]')
        plotz.set_ylabel(r'$\theta_{Science Park}$ [\si{\degree}]')
        plotz.set_xticks([0, 15, 30, 45, 60])
        plotz.set_yticks([0, 15, 30, 45, 60])
        plotz.save_as_pdf('zenith_501_spa_minn%d' % minn)

        distances = angle_between(zens.compress(filter), azis.compress(filter),
                                  zenc.compress(filter), azic.compress(filter))
        counts, bins = np.histogram(distances, bins=np.linspace(0, np.pi, 91))
        plotd = Plot()
        plotd.histogram(counts, np.degrees(bins))
        sigma = np.degrees(np.percentile(distances[np.isfinite(distances)], 67))
        plotd.set_label(r'67\%% within \SI{%.1f}{\degree}' % sigma)
        # plotd.set_title('Distance between reconstructed angles for station and cluster')
        plotd.set_xlabel('Angle between reconstructions [\si{\degree}]')
        plotd.set_ylabel('Counts')
        plotd.set_xlimits(min=0, max=90)
        plotd.set_ylimits(min=0)
        plotd.save_as_pdf('angle_between_501_spa_minn%d' % minn)


if __name__ == '__main__':
    # with tables.open_file(DATA_PATH, 'a') as data:
    #     reconstruct_data(data)
    with tables.open_file(DATA_PATH, 'r') as data:
        analyse_reconstructions(data)
