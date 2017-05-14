import os

from sapphire import CorsikaQuery, qsub

OVERVIEW = '/data/hisparc/corsika/corsika_overview.h5'
SCRIPT = """\
#!/usr/bin/env bash
python /data/hisparc/adelaat/corsika_accuracy/simulation_station_time.py {seeds}
"""


if __name__ == "__main__":
    cq = CorsikaQuery(OVERVIEW)
    for e in [15, 15.5, 16, 16.5, 17]:
        sims = cq.simulations(zenith=0, energy=e, particle='proton')
        seeds_set = set(cq.seeds(sims))
        print e
        for n in range(min(20, len(seeds_set), qsub.check_queue('generic'))):
            seeds = seeds_set.pop()
            if os.path.exists('%s.h5' % seeds):
                continue
            print seeds,
            qsub.submit_job(SCRIPT.format(seeds=seeds),
                            'cors_accu_%s' % seeds, 'generic')
    cq.finish()
