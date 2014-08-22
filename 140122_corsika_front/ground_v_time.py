import os

import tables
import numpy
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


SEED_NUMBERS = '231360773_763934896'
DATA_PATH = '/Users/arne/Datastore/CORSIKA'
DATA_FILE = os.path.join(DATA_PATH, SEED_NUMBERS, 'corsika.h5')

QUERY_DETECTABLE = ('((particle_id == 2) | (particle_id == 3) | '
                    ' (particle_id == 5) | (particle_id == 6))')
QUERY_TIMESLICE = ('(t >= %s) & (t < %s)')


def plot_time_slices(data):
    groundparticles = data.getNode('/', 'groundparticles')
    filtered_particles = groundparticles.getWhereList(QUERY_DETECTABLE + ' & (r < 4000)')
    times = groundparticles.readCoordinates(filtered_particles, field='t')
    header = groundparticles._v_attrs.event_header
    step = 2000
    for t in range(times.min(), times.max(), step):
        QUERY = QUERY_DETECTABLE + ' & ' + QUERY_TIMESLICE % (t, t + step)
        filtered_particles = groundparticles.getWhereList(QUERY)
        detectable_x = groundparticles.readCoordinates(filtered_particles, field='x')
        detectable_y = groundparticles.readCoordinates(filtered_particles, field='y')
        plt.figure()
        plt.title('Energy: %g eV, Zenith: %.1f' % (header.energy, header.theta_max))
        plt.xlabel('x (m)')
        plt.ylabel('y (m)')
        plt.annotate('%d < t < %d ns' % (t - times.min(), t - times.min() + step), (0.05, 0.8), xycoords='axes fraction')
        plt.axis('equal')
        plt.hist2d(detectable_x, detectable_y, bins=range(-4000, 4000, 50), cmap='binary', norm=LogNorm(vmin=0.2, vmax=5000, clip=True))
        plt.colorbar()
        plt.show()

if __name__ == '__main__':
    with tables.openFile(DATA_FILE, 'r') as data:
        plot_time_slices(data)
