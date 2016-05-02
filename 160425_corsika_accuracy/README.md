# 160425 - Analyse shower front using CORSIKA simulations

## Selecting CORSIKA simluations

    from sapphire import CorsikaQuery
    OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'
    cq = CorsikaQuery(OVERVIEW)
    for e in [14, 15, 16]:
        for p in ['proton', 'iron', 'gamma']:
            sims = cq.simulations(zenith=0, energy=e, particle=p)
            print sorted((s['first_interaction_altitude'],
                          s['n_electron'] + s['n_muon'],
                          '%d_%d' % (s['seed1'], s['seed2']))
                          for s in sims)[len(sims) / 2]

### Selected showers

    e = 14
    proton (21407, 12398,   '651000510_222963176')
    iron   (32160, 3111,    '155366293_265066277')
    gamma  (22301, 4519,    '758294490_567681579')

    e = 15
    proton (21838, 236165,  '791363922_262129855')
    iron   (32217, 53015,   '291305112_897286854')
    gamma  (21605, 102752,  '683790878_143722028')

    e = 16
    proton (22385, 1362702, '149042664_130233131')
    iron   (32552, 808941,  '108507276_832136747')
    gamma  (23418, 1922334, '458273069_189490816')


### Retrieving simulations

    seeds=758294490_567681579 && mkdir ${seeds} && scp adelaat@login2.nikhef.nl:/data/hisparc/corsika/data/${seeds}/corsika.h5 ${seeds}/


## Examine reconstruction accuracy versus density and core distance

With `simulation.py` the reconstruction accuracy of a shower from Zenith is
examined. It is plotted against the shower core distance and detected particle
density. As expected at large core distances the accuracy decreases as the
particle density also decreases and the probability increases that a detector
sees a particle later in the shower front.


## Examine termporal shower profile

Using `shower_front_profile.py` the shower front profile is examined for
various core distance bins. The electron/gamma profiles seem very similar for
the median showers for log E = 14.5, 15, and 16.


## Check chosen energy thresholds by looking at particle energy distritbution

Histogram particle E distribution for muons/electrons/gammas, mainly for muons to show lower energy muons are not seen. Reason for e/gamma E cut is detection chance (3 MeV) of e/gamma in detector.

Electrons/Gammas show clear cut at ~3 MeV, not all particles exhausted, so some are cut, but would not have large signal in detector.

Muons less clear cut, some cut, but should be quickly absorbed..


## TODOs

- Arrival t vs particle E for bin. Are low energy particles later?

- Same plots of shower profile as before for gamma and iron primaries. See if it behaves similar.

- Examine front shape as function of energy (different sizes) and interaction altitudes. Do for 15/16 with high statistics, see if 17/18 are within expectations.

- 





## Reference material

Grieder 2010 EAS - Chapter 9
