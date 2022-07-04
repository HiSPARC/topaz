import tables

from sapphire.corsika.store_corsika_data import copy_and_sort_node

PATH = "/Volumes/Tendrando Arms/Corsika_datastore/%s/"
SOURCE = PATH + 'corsika_unsorted.h5'
TARGET = PATH + 'corsika.h5'
seeds = ['137072066_411190751', '469096318_149263382', '686616026_423396879', '870131152_235443703']

if __name__ == "__main__":
    for seed in seeds:
        temp_path = SOURCE % seed
        destination = TARGET % seed
        with tables.open_file(temp_path, 'r') as hdf_temp, tables.open_file(destination, 'w') as hdf_data:
            copy_and_sort_node(hdf_temp, hdf_data)
