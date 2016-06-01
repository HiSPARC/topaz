# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 15:34:43 2015

@author: Sabine
"""
import tables
import sapphire
from sapphire.analysis.coincidence_queries import CoincidenceQuery

# 0.1 Open de te analyseren data-file in een nieuwe filename.
# In deze file dienen coincidenties en gereconstrueerde coincidenties
# opgeslagen te zijn
srcfile = 'Data_N6_feb10feb15.h5'
dstfile = ('Data_N6_feb10feb15_selectie' +
           datetime.datetime.now().strftime("%Y%m%d-%H%M") + '.h5')
# stationnummers opgeven die in de datafile voorkomen
stations = [501, 502, 503, 504, 505, 509]
# Maak een kopie van de te analyseren gegevens en werk daar in verder
tables.copy_file(srcfile, dstfile, overwrite=False)

data_write = tables.open_file(dstfile, 'a')

description = {'id': tables.UInt32Col(pos=0),
               'timestamp': tables.Time32Col(pos=1),
               'nanoseconds': tables.UInt32Col(pos=2),
               'ext_timestamp': tables.UInt64Col(pos=3),
               'N': tables.Int16Col(pos=4),
               'x': tables.Int32Col(pos=5),
               'y': tables.Float32Col(pos=6),
               'zenith': tables.Float32Col(pos=7),
               'azimuth': tables.Float32Col(pos=8),
               'snum_highintegral': tables.Float32Col(pos=9),
               'pulse_integral': tables.Float32Col(pos=10, shape=4),
               'size': tables.Float32Col(pos=11),
               'energy': tables.Float32Col(pos=12),
               'pulseints_s501': tables.Float32Col(pos=13, shape=4),
               'pulseints_s502': tables.Float32Col(pos=14, shape=4),
               'pulseints_s503': tables.Float32Col(pos=15, shape=4),
               'pulseints_s504': tables.Float32Col(pos=16, shape=4),
               'pulseints_s505': tables.Float32Col(pos=17, shape=4),
               'pulseints_s509': tables.Float32Col(pos=18, shape=4)}


# Nu eerst een tabel met grote showers maken die geselecteerd zijn op
# maximale pulswaarde van deelnemende stations
data_write.create_table('/bigshowers', 'bigshowers_maxpulseint',
                        description, createparents=True)

cq = CoincidenceQuery(srcfile)
coinc_analyse = cq.all(stations)
events = cq.all_events(coinc_analyse)

coincidences = data_write.get_node('/bigshowers', 'bigshowers_maxpulseint')
row = coincidences.row

m = 0
for event in events:
    n = 0
    pulseints_stations = {'s%d' % s: [] for s in stations}
    for station in range(0, len(stations)):
        temp = event[station]
        snum = temp[0]
        # LET OP!! VOLGORDE VAN AFHANDELEN IN DE COINCIDENCE QUERY LIJKT
        # WILLEKEURIG, GAAT NIET OP OPLOPEND STATION-NUMBER!
        specs = temp[1]
        pulseints_stations["s{0}".format(snum)] = specs[5]

    for station in range(0, len(stations)):
        temp = event[station]
        snum = temp[0]
        # LET OP!! VOLGORDE VAN AFHANDELEN IN DE COINCIDENCE QUERY LIJKT
        # WILLEKEURIG, GAAT NIET OP OPLOPEND STATION-NUMBER!
        specs = temp[1]
        ints = specs[5]
        recs = data_write.root.coincidences.reconstructions
        for x in ints:
            if x > 200000:
                # Verantwoording 200000; zie bestand 'Verantwoording van de
                # grenswaardes'
                id_ = cq.coincidences.col('id')[m]
                if recs.read_where('id==id_', field='zenith'):
                    # Schrijf coïncidentie alleen weg als deze succesvol is
                    # gereconstrueerd
                    row['id'] = id_
                    row['N'] = cq.coincidences.col('N')[m]
                    row['timestamp'] = cq.coincidences.col('timestamp')[m]
                    row['nanoseconds'] = cq.coincidences.col('nanoseconds')[m]
                    row['ext_timestamp'] = cq.coincidences.col('ext_timestamp')[m]
                    row['zenith'] = recs.read_where('id==id_', field='zenith')
                    row['azimuth'] = recs.read_where('id==id_', field='azimuth')
                    row['snum_highintegral'] = snum
                    row['pulse_integral'] = ints
                    row['pulseints_s501'] = pulseints_stations['s501']
                    row['pulseints_s502'] = pulseints_stations['s502']
                    row['pulseints_s503'] = pulseints_stations['s503']
                    row['pulseints_s504'] = pulseints_stations['s504']
                    row['pulseints_s505'] = pulseints_stations['s505']
                    row['pulseints_s509'] = pulseints_stations['s509']
                    row.append()
                    break
                else:
                    n = 0
            else:
                n = 0
    m += 1


# Nu tweede tabel maken met grote showers gebaseerd op maximale pulse
# integraal waarbij het staion met maximale pulse integraal niet meedoet
# in de som
description = {'id': tables.UInt32Col(pos=0),
               'timestamp': tables.Time32Col(pos=1),
               'nanoseconds': tables.UInt32Col(pos=2),
               'ext_timestamp': tables.UInt64Col(pos=3),
               'N': tables.Int16Col(pos=4),
               'x': tables.Int32Col(pos=5),
               'y': tables.Float32Col(pos=6),
               'zenith': tables.Float32Col(pos=7),
               'azimuth': tables.Float32Col(pos=8),
               'all_pulsints': tables.Float32Col(pos=9, shape=20),
               'sum_pulsints': tables.Float32Col(pos=10),
               'size': tables.Float32Col(pos=11),
               'energy': tables.Float32Col(pos=12),
               'pulseints_s501': tables.Float32Col(pos=13, shape=4),
               'pulseints_s502': tables.Float32Col(pos=14, shape=4),
               'pulseints_s503': tables.Float32Col(pos=15, shape=4),
               'pulseints_s504': tables.Float32Col(pos=16, shape=4),
               'pulseints_s505': tables.Float32Col(pos=17, shape=4),
               'pulseints_s509': tables.Float32Col(pos=18, shape=4)}
data_write.create_table('/bigshowers', 'sum_pulseint_zonderzwarestation',
                        description, createparents=True)

cq = CoincidenceQuery(srcfile)
coinc_analyse = cq.all([501, 502, 503, 504, 505, 509])
events = cq.all_events(coinc_analyse)

coincidences = data_write.get_node(
    '/bigshowers', 'sum_pulseint_zonderzwarestation')
row = coincidences.row
m = 0
sum_pulsints = []

for event in events:
    n = 0
    test = 0
    all_pulsints = []

    ints_stations = {'s%d' % s: [] for s in stations}
    for station in range(0, len(stations)):
        temp = event[station]
        specs = temp[1]
        ints = specs[5]
        # lees wat voor dit station de maximale waarde van de puls-integraal is
        test_t = max(ints)
        # LET OP!! VOLGORDE VAN AFHANDELEN IN DE COINCIDENCE QUERY LIJKT
        # WILLEKEURIG, GAAT NIET OP OPLOPEND STATION-NUMBER!
        snum = temp[0]
        ints_stations["s{0}".format(snum)] = specs[5]

        if test_t > test:
            # Als maximale waarde pulseintegraal groter dan eerder geanalyseerd
            # station, dan deze opslaan
            test = test_t
            # Ook regelnummer (identificeert station) opslaan waarin maximale
            # pulse-int zich bevindt
            n = station
        else:
            n = n
            test = test

    # Na bovenstaande for-loop weet je wat de maximale pulse-integraal is voor de deelnemende stations in coincidentie
    # In n heb je ook opgeslagen in welke regel (en dus station) het maximum optreedt
    # Nu opnieuw voor dezelfde coïncidentie over de stations (events) loopen
    for station in range(0, len(stations)):
        temp = event[station]
        specs = temp[1]
        ints = specs[5]

        if station == n:
            # Als je bij het station komt waarin het maximum zich bevindt dan
            # niets overnemen
            all_pulsints = all_pulsints
        else:
            for p in ints:
                all_pulsints.append(p)
                # voor alle stations zonder het maximum, de pulse-integralen
                # achter elkaar zetten

    sum_int = sum(all_pulsints)
    # Sommeren over alle puls-integralen voor deze coïncidentie
    sum_pulsints.append(sum_int)

    # deze loop loopt over het aantal coïncidenties in je datafile;
    # uiteindelijk moet sum_pulsints dus net zo lang zijn als het aantal
    # coïncidenties dat je hebt

    if sum_int > 600000:
        # Verantwoording 600000; zie 'maximale pulshoogte per station in 1
        # maand - conclusie 200000 -> data uit februari 2014
        id_ = cq.coincidences.col('id')[m]
        recs = data_write.root.coincidences.reconstructions
        if recs.read_where('id==id_', field='zenith'):
            # Ook hier coïncidentie alleen wegschrijven als aan voorwaarde is
            # voldaan én de reconstructie succesvol is gereconstrueerd
            row['id'] = id_
            row['N'] = cq.coincidences.col('N')[m]
            row['timestamp'] = cq.coincidences.col('timestamp')[m]
            row['nanoseconds'] = cq.coincidences.col('nanoseconds')[m]
            row['ext_timestamp'] = cq.coincidences.col('ext_timestamp')[m]
            row['zenith'] = recs.read_where('id==id_', field='zenith')
            row['azimuth'] = recs.read_where('id==id_', field='azimuth')
            row['all_pulsints'] = all_pulsints
            row['sum_pulsints'] = sum_int
            row['pulseints_s501'] = ints_stations['s501']
            row['pulseints_s502'] = ints_stations['s502']
            row['pulseints_s503'] = ints_stations['s503']
            row['pulseints_s504'] = ints_stations['s504']
            row['pulseints_s505'] = ints_stations['s505']
            row['pulseints_s509'] = ints_stations['s509']
            row.append()
    m += 1

data_write.close()

# Nu derde tabel maken met ids van showers die in beide datasets voorkomen
data_write = tables.open_file(dstfile, 'a')
description = {'id': tables.UInt32Col(pos=0)}
data_write.create_table('/bigshowers', 'selection',
                        description, createparents=True)
selectie = data_write.get_node('/bigshowers', 'selection')
row = selectie.row

tabel1 = data_write.root.bigshowers.bigshowers_maxpulseint
tabel2 = data_write.root.bigshowers.sum_pulseint_zonderzwarestation

if len(tabel1) >= len(tabel2):
    ids = data_write.root.bigshowers.sum_pulseint_zonderzwarestation.col('id')
    id_check = data_write.root.bigshowers.bigshowers_maxpulseint.col('id')

    for i in ids:
        if i in id_check:
            row['id'] = i
            row.append()

elif len(tabel2) > len(tabel1):
    ids = data_write.root.bigshowers.bigshowers_maxpulseint.col('id')
    id_check = data_write.root.bigshowers.sum_pulseint_zonderzwarestation.col('id')

    for i in ids:
        if i in id_check:
            row['id'] = i
            row.append()

data_write.close()
