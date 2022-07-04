from datetime import datetime as dt


class Tijdtest():

    def __init__(self, id, hisparc, gps, trigger, start, end, note):
        self.id = id
        self.hisparc = hisparc
        self.gps = gps
        self.trigger = trigger
        self.group = "/".join((hisparc, gps, trigger))
        if note:
            self.legend = "%03d %s/%s/%s+" % (id, hisparc, gps, trigger)
        else:
            self.legend = "%03d %s/%s/%s" % (id, hisparc, gps, trigger)
        self.start = dt(*start)
        self.end = dt(*end)
        self.time = (self.start, self.end)
        self.note = note


def test_log():
    """ A log of all tests

    In this program is a list of all available tests from the tijdtest
    project.

    """
    # id HiSPARC GPS    Trigger  Start datetime       End datetime         Notes
    tests = (
        (1, '083', '501', 'PMT2', (2011, 11, 15, 15, 52), (2011, 11, 16, 14, 25), 'int250'),
        (2, '074', '501', 'PMT2', (2011, 11, 16, 14, 44), (2011, 11, 17, 15, 6), ''),
        (3, '074', '501', 'PMT2', (2011, 11, 17, 15, 9), (2011, 11, 18, 14, 49), 'bgps100'),
        (4, '018', '501', 'PMT2', (2011, 11, 18, 15, 46), (2011, 11, 21, 7, 25), ''),
        (5, '156', '501', 'PMT2', (2011, 11, 21, 7, 27), (2011, 11, 22, 9, 14), 'mas018'),
        (6, '074', '501', 'EXT', (2011, 11, 22, 9, 30), (2011, 11, 23, 9, 38), ''),
        (7, '050', '501', 'PMT2', (2011, 11, 23, 10, 58), (2011, 11, 23, 13, 40), 'noalmanac'),
        (8, '050', '501', 'PMT2', (2011, 11, 23, 13, 41), (2011, 11, 23, 14, 26), 'int250'),
        (9, '050', '501', 'EXT', (2011, 11, 23, 14, 28), (2011, 11, 23, 14, 58), 'int250'),
        (10, '050', '501', 'PMT2', (2011, 11, 23, 15, 0), (2011, 11, 24, 13, 18), ''),
        (11, '065', '501', 'PMT2', (2011, 11, 24, 13, 24), (2011, 11, 25, 11, 48), 'noalmanac'),
        (12, '176', '501', 'PMT2', (2011, 11, 25, 12, 3), (2011, 11, 26, 14, 47), ''),
        (13, '176', '501', 'PMT1', (2011, 11, 26, 14, 54), (2011, 11, 27, 14, 22), ''),
        (14, '176', '501', 'EXT', (2011, 11, 27, 14, 26), (2011, 11, 28, 14, 56), ''),
        (15, '122', '501', 'PMT2', (2011, 11, 28, 15, 15), (2011, 11, 29, 13, 27), ''),
        (16, '012', '501', 'PMT2', (2011, 11, 29, 13, 41), (2011, 11, 30, 13, 58), ''),
        (17, '040', '501', 'PMT2', (2011, 11, 30, 14, 12), (2011, 12, 1, 15, 30), ''),
        (18, '040', 'test', 'PMT2', (2011, 12, 1, 15, 45), (2011, 12, 2, 11, 38), 'r501'),
        (19, '083', 'test', 'PMT2', (2011, 12, 2, 15, 49), (2011, 12, 4, 21, 54), 'r501'),
        (20, '083', 'test', 'EXT', (2011, 12, 4, 22, 0), (2011, 12, 8, 11, 9), 'r501'),
        (21, '083', '501', 'PMT1', (2011, 12, 8, 11, 15), (2011, 12, 9, 11, 56), 'rbgps25'),
        (22, '083', '501', 'PMT2', (2011, 12, 9, 11, 58), (2011, 12, 13, 9, 11), 'rbgps25'),
        (23, '083', '501', 'EXT', (2011, 12, 13, 9, 14), (2011, 12, 19, 13, 52), 'rbgps25'),
        (24, '053', '501', 'PMT2', (2011, 12, 20, 15, 33), (2011, 12, 21, 20, 0), 'rbgps25'),
        (25, '053', '501', 'PMT2', (2012, 1, 9, 11, 14), (2012, 1, 10, 9, 28), ''),
        (26, '053', '501', 'EXT', (2012, 1, 10, 9, 32), (2012, 1, 11, 11, 32), 'rext'),
        (27, '053', '501', 'EXT', (2012, 1, 11, 11, 34), (2012, 1, 12, 14, 0), ''),
        (28, '053', '501', 'PMT2', (2012, 1, 12, 14, 3), (2012, 1, 13, 14, 20), 'rext'),
        (29, '053', 'test', 'PMT2', (2012, 1, 13, 14, 30), (2012, 1, 15, 17, 48), 'r501'),
        (30, '053', 'test', 'EXT', (2012, 1, 15, 17, 58), (2012, 1, 17, 11, 7), 'r501'),
        (31, '053', 'test', 'EXT', (2012, 1, 17, 11, 10), (2012, 1, 18, 13, 23), 'rext r501'),
        (32, '053', 'test', 'PMT2', (2012, 1, 18, 13, 26), (2012, 1, 19, 9, 26), 'rext r501'),
        (33, '018', 'test', 'PMT1', (2012, 5, 9, 15, 15), (2012, 5, 10, 11, 13), ''),
        (34, '050', 'test', 'PMT1', (2012, 5, 10, 11, 50), (2012, 5, 11, 15, 3), ''),
        (35, '050', 'test', 'PMT1', (2012, 5, 11, 15, 10), (2012, 5, 12, 22, 45), ''),
        (36, '050', 'test', 'EXT', (2012, 5, 12, 22, 59), (2012, 5, 13, 0, 0), ''),
        (37, '050', 'test', 'PMT2', (2012, 5, 31, 14, 24), (2012, 6, 4, 14, 0), ''),
        (38, '318', 'test', 'PMT2', (2012, 6, 12, 15, 13), (2012, 6, 18, 15, 0), 'unmod'),
        (39, '301', 'test', 'PMT1', (2012, 7, 17, 14, 16), (2012, 7, 18, 12, 12), ''),
        (40, '321', 'test', 'PMT1', (2012, 7, 18, 12, 16), (2012, 7, 19, 13, 32), 'mas301'),
        (41, '301', 'test', 'EXT', (2012, 7, 19, 13, 35), (2012, 7, 23, 10, 0), ''),
        (42, '328', 'test', 'PMT1', (2012, 7, 24, 13, 15), (2012, 7, 28, 12, 33), 'mas301'),
        (43, '328', 'test', 'PMT2', (2012, 7, 30, 9, 13), (2012, 8, 7, 14, 40), 'mas301 gpslost'),
        (44, '328', 'test', 'PMT2', (2012, 8, 7, 14, 45), (2012, 8, 29, 13, 35), 'mas301 bgps55'),
        (45, '344', 'test', 'PMT1', (2012, 8, 29, 14, 0), (2012, 8, 30, 12, 5), ''),
        (46, '318', 'test', 'PMT1', (2012, 8, 30, 12, 15), (2012, 8, 31, 12, 5), ''),
        (47, '305', 'test', 'PMT1', (2012, 8, 31, 12, 15), (2012, 9, 3, 12, 15), ''),
        (48, '305', 'test', 'PMT1', (2012, 9, 3, 12, 40), (2012, 9, 4, 11, 25), 'longgps'),
        (49, '341', 'test', 'PMT1', (2012, 9, 5, 13, 25), (2012, 9, 6, 12, 5), 'longgps'),
        (50, '341', 'test', 'PMT1', (2012, 9, 6, 12, 10), (2012, 9, 6, 13, 5), 'longgps ppsoff115'),
        (51, '341', 'test', 'PMT1', (2012, 9, 6, 13, 15), (2012, 9, 7, 10, 40), ''),
        (52, '310', 'test', 'PMT1', (2012, 9, 7, 11, 0), (2012, 9, 11, 14, 35), ''),
        (53, '310', 'test', 'PMT1', (2012, 9, 11, 14, 40), (2012, 9, 12, 8, 50), 'ppsoff-50'),
        (54, '345', 'test', 'PMT1', (2012, 9, 12, 9, 5), (2012, 9, 14, 13, 0), ''),
        (55, '352', 'test', 'PMT1', (2012, 9, 14, 13, 15), (2012, 9, 17, 8, 40), ''),
        (56, '353', 'test', 'PMT1', (2012, 9, 18, 8, 55), (2012, 9, 19, 8, 40), ''),
        (57, '099', 'test', 'PMT1', (2012, 9, 19, 14, 15), (2012, 9, 23, 14, 0), ''),
        (58, '160', 'test', 'PMT1', (2012, 12, 12, 14, 50), (2013, 1, 7, 12, 50), ''),
        (59, '160', 'test', 'PMT1', (2013, 1, 7, 13, 0), (2013, 1, 7, 14, 30), '2high1'),
        (60, '160', 'test', 'PMT2', (2013, 1, 7, 14, 36), (2013, 1, 7, 14, 55), '2high2'),
        (61, '341', 'test', 'PMT1', (2013, 1, 9, 10, 0), (2013, 1, 9, 13, 30), 'gpsrec85774017'),
        (62, '341', 'test', 'PMT1', (2013, 1, 9, 14, 5), (2013, 1, 9, 14, 30), 'noalmanac gpsrec01417277'),
        (63, '042', 'test', 'PMT2', (2013, 1, 9, 16, 20), (2013, 1, 10, 12, 35), 'mas043 3high3 int500'),
        (64, '042', 'test', 'PMT1', (2013, 1, 10, 12, 37), (2013, 1, 10, 12, 55), 'mas043 3high3'),
        (65, '043', 'test', 'PMT1', (2013, 1, 10, 12, 57), (2013, 1, 10, 13, 17), 'slv042 3high2'),
        (66, '341', 'test', 'PMT1', (2013, 1, 10, 13, 48), (2013, 1, 10, 14, 0), 'gpsrec81408050'),
        (67, '341', 'test', 'PMT1', (2013, 1, 10, 14, 3), (2013, 1, 10, 14, 15), 'noalmanac gpsrec01417271'),
        (68, '341', 'test', 'PMT1', (2013, 1, 10, 14, 22), (2013, 1, 10, 15, 0), 'noalmanac gpsrec81407713'),
        (69, '341', 'test', 'PMT1', (2013, 1, 10, 15, 13), (2013, 1, 10, 15, 25), 'sbgps204'),
        (70, '341', 'test', 'PMT1', (2013, 1, 17, 12, 50), (2013, 1, 17, 13, 56), ''),
        (71, '341', 'test', 'PMT1', (2013, 1, 17, 13, 58), (2013, 1, 17, 14, 42), 'noalmanac'),
        (72, '341', 'test', 'PMT1', (2013, 1, 17, 14, 44), (2013, 1, 24, 11, 49), 'noalmanac'),
        (73, '322', 'test', 'PMT1', (2013, 10, 31, 11, 0o3), (2013, 10, 31, 12, 28), ''),
        (74, '323', 'test', 'PMT1', (2013, 10, 31, 12, 34), (2013, 10, 31, 14, 9), 'noalmanac'),
        (75, '346', 'test', 'PMT1', (2013, 10, 31, 14, 14), (2013, 10, 31, 14, 48), 'noalmanac'),
        # ( 76, '343', 'test', 'PMT1', (2013,11, 4, 11,26), (2013,11, 4, 12,35), 'nodata'),
        (77, '303', 'test', 'PMT1', (2013, 11, 4, 16, 0o2), (2013, 11, 5, 10, 6), ''),
        (78, '307', 'test', 'PMT1', (2013, 11, 5, 10, 38), (2013, 11, 5, 11, 13), 'noalmanac'),
        (79, '311', 'test', 'PMT1', (2013, 11, 5, 11, 34), (2013, 11, 5, 12, 10), 'noalmanac'),
        (80, '313', 'test', 'PMT1', (2013, 11, 5, 12, 15), (2013, 11, 5, 13, 7), 'noalmanac'),
        (81, '343', 'test', 'PMT1', (2013, 11, 5, 13, 16), (2013, 11, 5, 13, 37), ''),
        (82, '304', 'test', 'PMT1', (2013, 11, 5, 13, 43), (2013, 11, 5, 14, 26), 'noalmanac'),
        (83, '050', '501', 'PMT2', (2011, 11, 23, 11, 5), (2011, 11, 23, 13, 40), 'subset7'),
        (84, '065', '501', 'PMT2', (2011, 11, 24, 13, 33), (2011, 11, 25, 11, 48), 'subset11'),
        (85, '341', 'test', 'PMT1', (2013, 1, 9, 14, 20), (2013, 1, 9, 14, 30), 'subset62 gpsrec01417277'),
        (86, '341', 'test', 'PMT1', (2013, 1, 10, 14, 10), (2013, 1, 10, 14, 15), 'subset67 gpsrec01417271'),
        (87, '341', 'test', 'PMT1', (2013, 1, 10, 14, 35), (2013, 1, 10, 15, 0), 'subset68 gpsrec81407713'),
        (88, '341', 'test', 'PMT1', (2013, 1, 17, 14, 10), (2013, 1, 17, 14, 42), 'subset71'),
        (89, '341', 'test', 'PMT1', (2013, 1, 17, 14, 47), (2013, 1, 24, 11, 49), 'subset72'),
        (90, '323', 'test', 'PMT1', (2013, 10, 31, 12, 43), (2013, 10, 31, 14, 9), 'subset74'),
        (91, '346', 'test', 'PMT1', (2013, 10, 31, 14, 23), (2013, 10, 31, 14, 48), 'subset75'),
        (92, '307', 'test', 'PMT1', (2013, 11, 5, 10, 43), (2013, 11, 5, 11, 13), 'subset78'),
        (93, '311', 'test', 'PMT1', (2013, 11, 5, 11, 40), (2013, 11, 5, 12, 10), 'subset79'),
        (94, '313', 'test', 'PMT1', (2013, 11, 5, 12, 22), (2013, 11, 5, 13, 7), 'subset80'),
        (95, '304', 'test', 'PMT1', (2013, 11, 5, 13, 50), (2013, 11, 5, 14, 26), 'subset82'))

    test_all = [Tijdtest(*test) for test in tests]

    return test_all


def get_tests(id=None, hisparc=None, gps=None, trigger=None, group=None,
              note=None, subset='ALL', complement=False, part=None,
              unique=True):
    """ Search available tests and return those that match request

    Tests can be retrieved based on their parameters.
    The HiSPARC box number, the GPS used and the trigger of the swapped box.

    Some special cases exist;
    the pulse generator was set at an interval of # ms (int#)
    the reference used the external trigger (rext)
    the reference used the 501 gps (r501)
    the GPS position of the reference was set incorrectly by # m (rbgps#)
    the GPS position of the swap was set incorrectly by # m (sbgps#)
    the swap was a slave connected to master # (slv###)
    a longer gps cable was used for the swap box (longgps)
    the PPS offset in DSPMon was set for the swap at # ns (ppsoff#)
    the swap lost the GPS connection was lost during the test (gpslost)
    the swap started the test with a cold GPS, without almanac (noalmanac)
    subset of another test to cut the part without almanac (subset##)

    """
    # All tests from the TijdTest Log
    test_all = test_log()

    # Select a subset
    if subset in ('ALL'):
        test_list = test_all
    elif subset in ('PMT'):
        test_list = [test for test in test_all
                     if ('PMT') in test.trigger and
                        ('rext') not in test.note and
                        ('bgps') not in test.note and
                        ('ppsoff') not in test.note and
                        ('longgps') not in test.note and
                        ('noalmanac') not in test.note]
    elif subset in ('EXT'):
        test_list = [test for test in test_all
                     if ('EXT') in test.trigger or
                        ('rext') in test.note]
    elif subset in ('GPS'):
        test_list = [test for test in test_all
                     if ('test') in test.gps or
                        ('r501') in test.note]
    elif subset in ('ownGPS'):
        test_list = [test for test in test_all
                     if (('test') in test.gps and
                         ('r501') in test.note) or
                        (('501') in test.gps and
                         ('r501') not in test.note)]
    elif subset in ('sameGPS'):
        test_list = [test for test in test_all
                     if (('test') in test.gps and
                         ('r501') not in test.note) or
                        (('501') in test.gps and
                         ('r501') in test.note)]
    elif subset in ('Bad'):
        test_list = [test for test in test_all
                     if ('sbgps') in test.note or
                        ('rbgps') in test.note]
    elif subset in ('SLV'):
        test_list = [test for test in test_all
                     if ('slv') in test.note]
    elif subset in ('NoAlmanac'):
        test_list = [test for test in test_all
                     if ('noalmanac') in test.note]
    elif subset in ('Good1'):
        # Tests with different GPS, otherwise normal conditions
        test_list = [test for test in test_all
                     if test.id in [1, 2, 4, 10, 12, 15, 16, 17, 25, 84]]
    elif subset in ('Good2'):
        # Tests with GPS splitter, otherwise normal conditions
        # test 33 and 34 could be added, but the same units were also
        # tested with a different GPS: 4 and 10, which are in Good1
        test_list = [test for test in test_all
                     if test.id in [33, 34,
                                    38, 39, 45, 47, 51, 52, 54, 55, 56, 57, 58,
                                    73, 77, 81, 90, 91, 92, 93, 94, 95]]
    else:
        test_list = test_all

    if complement and subset in ('EXT'):
        test_list = [test
                     for test in test_all
                     for ptest in test_list
                     if test.group == ptest.group.replace('EXT', 'PMT2') or
                     test.group == ptest.group.replace('EXT', 'PMT1') or
                     test.group == ptest.group]
    elif complement and subset in ('GPS'):
        test_list = [test
                     for test in test_all
                     for ptest in test_list
                     if test.group == ptest.group.replace('test', '501') or
                     test.group == ptest.group]
    elif complement and subset in ('Bad'):
        test_list = [test
                     for test in test_all
                     for ptest in test_list
                     if test.group == ptest.group]
    elif complement and subset in ('NoAlmanac'):
        for test in test_list:
            print('subset%d' % test.id)
        test_list = [test
                     for test in test_all
                     for ptest in test_list
                     if 'subset%d' % ptest.id in test.note or
                        test.id == ptest.id]

    if id:
        test_list = [test for test in test_list if id in [test.id]]
    if hisparc:
        test_list = [test for test in test_list if hisparc in [test.hisparc]]
    if gps:
        test_list = [test for test in test_list if gps in test.gps]
    if trigger:
        test_list = [test for test in test_list if trigger in test.trigger]
    if group:
        test_list = [test for test in test_list if group in test.group]
    if note:
        test_list = [test for test in test_list if note in test.note]

    # Get a part of the class
    if part in (None,):
        pass
    elif part in ('id',):
        test_list = [test.id for test in test_list]
    elif part in ('hisparc',):
        test_list = [test.hisparc for test in test_list]
    elif part in ('trigger',):
        test_list = [test.trigger for test in test_list]
    elif part in ('gps',):
        test_list = [test.gps for test in test_list]
    elif part in ('group',):
        test_list = [test.group for test in test_list]
    elif part in ('legend',):
        test_list = [test.legend for test in test_list]
    elif part in ('time',):
        test_list = [test.time for test in test_list]
    elif part in ('start',):
        test_list = [test.start for test in test_list]
    elif part in ('end',):
        test_list = [test.end for test in test_list]
    elif part in ('note',):
        test_list = [test.note for test in test_list]

    if unique:
        test_list = sorted(set(test_list))

    return test_list


if __name__ in ('__main__'):
    print(("Number of tests: %s (unique: %s)" %
           (len(get_tests(subset='ALL', unique=False)),
            len(get_tests(subset='ALL', unique=True)))))
    print(("Number of boxes: %s" %
           len(get_tests(part='hisparc', unique=True))))
    print(('HII:074:  %s' % ", ".join(get_tests(hisparc='074', part='group'))))
    print(('GPS:test: %s' % ", ".join(get_tests(gps='test', part='group'))))
    print(('TRG:EXT:  %s' % ", ".join(get_tests(trigger='EXT', part='group'))))
    print(('HII:053, TRG:EXT: %s' %
           ", ".join(get_tests(hisparc='053', trigger='EXT', part='group'))))
    print(('GRP:018/501/PMT2: %s' %
           ", ".join(get_tests(group='018/501/PMT2', part='group'))))
    print(("GPS:test +comp: %s" %
           ", ".join(get_tests(subset='GPS', part='hisparc'))))
    print(("BadGPS: %s" %
           ", ".join(get_tests(subset='Bad', part='hisparc'))))
    print(("TRG:EXT +comp: %s" %
           ", ".join(get_tests(subset='EXT', part='group', complement=True))))
