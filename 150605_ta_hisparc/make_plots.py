import healpy as hp
import os


SELF_PATH = os.path.dirname(__file__)
FILES = ['heal157-smeared.fits', 'heal553-smeared.fits',
         'heal785-smeared.fits', 'healdata-smeared.fits',
         'healflat-smeared.fits',
         'slm157.fits', 'slm553.fits', 'slm785.fits', 'slmflat.fits']
HISPARC = [os.path.join(SELF_PATH, 'hisparc-heal', F) for F in FILES]
TELEARR = [os.path.join(SELF_PATH, 'telarr-heal', F) for F in FILES]


hisparc_maps = [hp.read_map(hisparc_fits) for hisparc_fits in HISPARC]
telearr_maps = [hp.read_map(telearr_fits) for telearr_fits in TELEARR]

[hp.mollview(hisparc_map, title='HiSPARC events: %s' % F, cmap='coolwarm')
 for hisparc_map, F in zip(hisparc_maps, FILES)]
[hp.mollview(telearr_map, title='TELEARR events: %s' % F, cmap='coolwarm')
 for telearr_map, F in zip(telearr_maps, FILES)]

EXTRA = os.path.join(SELF_PATH, 'slmpixflat.fits')
extra_map = hp.read_map(EXTRA)
hp.mollview(extra_map, title='slmpixflat.fits')
