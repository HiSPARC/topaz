""" Perform simulations on the Science Park stations 501 through 506

These are the stations that Sabine used for her analysis.
The goal of these simulations is to see if an input of the zenith
distribution at the top of the atmosphere (uniform) results in the
detected zenith distribution on the ground.

"""

from __future__ import division

from sapphire.qsub import submit_job
from sapphire.utils import pbar


SCRIPT = """\
#!/usr/bin/env bash

python << END
import tables
from sapphire import ScienceParkCluster, MultipleGroundParticlesSimulation

cluster = ScienceParkCluster(range(501, 507))
result_path = '/data/hisparc/adelaat/cluster_efficiency/151014_{job_id}.h5'
overview = '/data/hisparc/corsika/corsika_overview.h5'

with tables.open_file(result_path, 'w') as data:
    sim = MultipleGroundParticlesSimulation(overview, 600, 1e16, 10**17.5, cluster=cluster,
                                            data=data, N=100, progress=False)
    sim.run()
    sim.finish()
END
"""


def perform_simulations():
    for id in pbar(range(10)):
        script = SCRIPT.format(job_id=id)
        submit_job(script, 'spa_sim_%d' % id, 'long')


if __name__ == "__main__":
    perform_simulations()
