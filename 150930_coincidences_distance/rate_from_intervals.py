from glob import glob
import os
import multiprocessing

from scipy.stats import linregress
from numpy import histogram, log, linspace, where, nan, mean
import tables

from sapphire import HiSPARCNetwork
from artist import Plot

PATH = '/Users/arne/Datastore/pairs/*_*.h5'


def determine_rates():
    paths = glob(PATH)
    worker_pool = multiprocessing.Pool()
    worker_pool.map(determine_rate, paths)
    worker_pool.close()
    worker_pool.join()


def determine_rate(path):
    file = os.path.basename(path)
    pair = tuple([int(s) for s in file[:-3].split('_')])

    net = HiSPARCNetwork(force_stale=True)
#     if net.calc_distance_between_stations(*pair) > 1e3:
#         print pair, 'far apart'

    with tables.open_file(path, 'r') as data:
        ets = data.root.coincidences.coincidences.col('ext_timestamp')

    dts = ets[1:] - ets[:-1]
    dts.sort()

    if len(dts) > 25:
        expected_interval = mean(dts[:-5])
    else:
        expected_interval = mean(dts)

    bins = linspace(0, 1.5 * expected_interval, 10)
    c, b = histogram(dts, bins=bins)
    x = (bins[1:] + bins[:-1]) / 2.
    filter = c > 0
    slope, intercept, r_value, _, _ = linregress(x[filter], log(c[filter]))
    print pair, expected_interval, 1e9 / expected_interval, r_value ** 2
    rate = slope * -1e9
    with tables.open_file(path, 'a') as data:
        data.set_node_attr('/', 'interval_rate', rate)
    # plot_fit(x, data, slope, intercept, pair)


def plot_fit(x, data, slope, intercept, pair):
    plot = Plot()
    plot.scatter(x, log(c))
    plot.plot(x, x * slope + intercept, mark=None)
    plot.set_ylimits(min=0)
    plot.set_label(r'%.1e \si{\hertz}' % rate)
    plot.save_as_pdf('intervals/intervals_%d_%d_r' % pair)


if __name__ == "__main__":
    determine_rates()
