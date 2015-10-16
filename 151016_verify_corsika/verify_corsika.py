import os

import tables

from sapphire.corsika.corsika_queries import CorsikaQuery


DATAPATH = '/data/hisparc/corsika/data/{seeds}/corsika.h5'


def verify_file(path):
    assert os.path.exists(path)


def verify_table(data):
    data.get_node('/', 'groundparticles')


def verify_attrs(data):
    data.get_node_attr('/', 'event_header')
    data.get_node_attr('/', 'event_end')
    data.get_node_attr('/', 'run_header')
    data.get_node_attr('/', 'run_end')


def verify_data():
    cq = CorsikaQuery('/data/hisparc/corsika/corsika_overview.h5')
    all_seeds = cq.seeds(cq.all_simulations(iterator=True), iterator=True)
    for seeds in all_seeds:
        path = DATAPATH.format(seeds=seeds)
        print '%20s' % seeds,
        try:
            verify_file(path)
            print '.',
        except AssertionError:
            # Skip next tests
            print 'E S S'
            continue

        with tables.open_file(path, 'r') as data:
            try:
                verify_table(data)
                print '.',
            except tables.NoSuchNodeError:
                print 'E',
            try:
                verify_attrs(data)
                print '.',
            except tables.AttributeError:
                print 'E',
        print


if __name__ == "__main__":
    verify_data()
