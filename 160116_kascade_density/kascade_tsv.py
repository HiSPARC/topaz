"""Compare predicted detector density to the detected number of particles"""

import csv

import tables

DATA_PATH = '/Users/arne/Datastore/kascade/kascade-reconstructions.h5'
OUTPUT_PATH = '/Users/arne/Datastore/kascade/kascade-reconstructions.tsv'


if __name__ == "__main__":
    output = open(OUTPUT_PATH, 'w')
    writer = csv.writer(output, delimiter='\t', lineterminator='\n')
    with tables.open_file(DATA_PATH) as data:
        recs = data.get_node('/reconstructions')
        colnames = recs.colnames
        output.write('# ' + '\t'.join(colnames) + '\n')
        writer.writerows(recs.read().tolist())

    output.close()
