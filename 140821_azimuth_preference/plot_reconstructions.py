import tables
from numpy import histogram, degrees, isnan

from artist import Plot

from sapphire import ReconstructESDEvents

with tables.open_file('/Users/arne/Datastore/esd/2013/10/2013_10_28.h5', 'r') as data:
    for s in [501, 502, 503, 504, 505, 506, 508, 509]:
        rec = ReconstructESDEvents(data, '/hisparc/cluster_amsterdam/station_%d' % s, s)
        rec.reconstruct_directions(detector_ids=[0, 2, 3])
        azimuths = [degrees(a) for a, z in zip(rec.phi, rec.theta)
                    if degrees(z) > 10 and not isnan(a)]
        n, bins = histogram(azimuths, bins=range(-180, 190, 10))
        graph = Plot()
        graph.histogram(n, bins)
        graph.set_title('Station %d' % s)
        graph.set_xlabel('Azimuth')
        graph.set_xlimits(-180, 180)
        graph.set_ylimits(min=0)
        graph.save_as_pdf('azimuths_123_s%d' % s)
