import matplotlib.pyplot as plt
import tables
from scipy.optimize import curve_fit

from sapphire.simulations.showerfront import (FlatFrontSimulation,
                                              FlatFrontSimulationWithoutErrors)
from sapphire.clusters import SingleTwoDetectorStation, SingleStation
from sapphire.analysis.reconstructions import ReconstructESDEvents
from sapphire.utils import gauss


cluster = SingleTwoDetectorStation()
station = cluster.stations[0]
detectors = station.detectors

sim_off = []
rec_off = []
zz = range(-20, 21, 2)

with tables.open_file('test_showerfront_alt.h5', 'w') as data:
    for z in zz:
        detectors[0].z = z
        sim = FlatFrontSimulation(cluster, data, '/e_z%d' % z, 20000)
        sim.run()
        # sim_off.append(
        events = sim.station_groups[0].events
        dt = events.col('t1') - events.col('t2')
        bins = arange(-100 + 1.25, 100, 2.5)
        y, bins = histogram(dt, bins=bins)
        x = (bins[:-1] + bins[1:]) / 2
        popt, pcov = curve_fit(gauss, x, y, p0=(len(dt), 0., 10.))

        rec_off.append(popt[1])

        print '% 3d: %f' % (z, popt[1])
        plt.figure()
        plt.hist(dt, bins=bins)
        plt.plot(x, gauss(x, *popt))
        plt.title('Z = %d' % z)
        plt.show()
