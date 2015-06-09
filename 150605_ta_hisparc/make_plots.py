import healpy as hp
import os

SELF_PATH = os.path.dirname(__file__)
FILES = ['heal157-smeared.fits', 'heal553-smeared.fits',
         'heal785-smeared.fits', 'healdata-smeared.fits',
         'healflat-smeared.fits',
         'slm157.fits', 'slm553.fits', 'slm785.fits', 'slmflat.fits']
HISPARC = [os.path.join(SELF_PATH, 'hisparc-heal', F) for F in FILES]
TELARR = [os.path.join(SELF_PATH, 'telarr-heal', F) for F in FILES]

hisparc_maps = [hp.read_map(hisparc_fits) for hisparc_fits in HISPARC]
telarr_maps = [hp.read_map(telarr_fits) for telarr_fits in TELARR]

[hp.mollview(hisparc_map, title='HiSPARC events: %s' % F) for hisparc_map, F in zip(hisparc_maps, FILES)]
[hp.mollview(telarr_map, title='TA events: %s' % F) for telarr_map, F in zip(telarr_maps, FILES)]
