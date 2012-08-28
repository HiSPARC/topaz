from datetime import datetime as dt
from re import sub


class Tijdtest():
    def __init__(self, id, hisparc, gps, trigger, start, end, note):
        self.id = id
        self.hisparc = hisparc
        self.gps = gps
        self.trigger = trigger
        self.group = "/".join((hisparc, gps, trigger))
        self.start = dt(*start)
        self.end = dt(*end)
        self.time = (self.start, self.end)
        self.note = note


def test_log():
    """ A log of all tests

    In this program is a list of all available tests from the tijdtest
    project.

    """
    tests = (
        (  1, '083', '501', 'PMT2',  (2011,11,15, 15,52), (2011,11,16, 14,25), 'int250'),
        (  2, '074', '501', 'PMT2',  (2011,11,16, 14,44), (2011,11,17, 15, 6), ''),
        (  3, '074', '501', 'PMT2',  (2011,11,17, 15, 9), (2011,11,18, 14,49), 'sbgps100'),
        (  4, '018', '501', 'PMT2',  (2011,11,18, 15,46), (2011,11,21,  7,25), ''),
        (  5, '156', '501', 'PMT2',  (2011,11,21,  7,27), (2011,11,22,  9,14), 'slv018'),
        (  6, '074', '501', 'EXT',   (2011,11,22,  9,30), (2011,11,23,  9,38), ''),
        (  7, '050', '501', 'PMT2',  (2011,11,23, 10,58), (2011,11,23, 13,40), ''),
        (  8, '050', '501', 'PMT2',  (2011,11,23, 13,41), (2011,11,23, 14,26), 'int250'),
        (  9, '050', '501', 'EXT',   (2011,11,23, 14,28), (2011,11,23, 14,58), 'int250'),
        ( 10, '050', '501', 'PMT2',  (2011,11,23, 15, 0), (2011,11,24, 13,18), ''),
        ( 11, '065', '501', 'PMT2',  (2011,11,24, 13,24), (2011,11,25, 11,48), ''),
        ( 12, '176', '501', 'PMT2',  (2011,11,25, 12, 3), (2011,11,26, 14,47), ''),
        ( 13, '176', '501', 'PMT1',  (2011,11,26, 14,54), (2011,11,27, 14,22), ''),
        ( 14, '176', '501', 'EXT',   (2011,11,27, 14,26), (2011,11,28, 14,56), ''),
        ( 15, '122', '501', 'PMT2',  (2011,11,28, 15,15), (2011,11,29, 13,27), ''),
        ( 16, '012', '501', 'PMT2',  (2011,11,29, 13,41), (2011,11,30, 13,58), ''),
        ( 17, '040', '501', 'PMT2',  (2011,11,30, 14,12), (2011,12, 1, 15,30), ''),
        ( 18, '040', 'test' ,'PMT2', (2011,12, 1, 15,45), (2011,12, 2, 11,38), 'r501'),
        ( 19, '083', 'test' ,'PMT2', (2011,12, 2, 15,49), (2011,12, 4, 21,54), 'r501'),
        ( 20, '083', 'test' ,'EXT',  (2011,12, 4, 22, 0), (2011,12, 8, 11, 9), 'r501'),
        ( 21, '083', '501', 'PMT1',  (2011,12, 8, 11,15), (2011,12, 9, 11,56), 'rbgps25'),
        ( 22, '083', '501', 'PMT2',  (2011,12, 9, 11,58), (2011,12,13,  9,11), 'rbgps25'),
        ( 23, '083', '501', 'EXT',   (2011,12,13,  9,14), (2011,12,19, 13,52), 'rbgps25'),
        ( 24, '053', '501', 'PMT2',  (2011,12,20, 15,33), (2011,12,21, 20, 0), 'rbgps25'),
        ( 25, '053', '501', 'PMT2',  (2012, 1, 9, 11,14), (2012, 1,10,  9,28), ''),
        ( 26, '053', '501', 'EXT',   (2012, 1,10,  9,32), (2012, 1,11, 11,32), 'rext'),
        ( 27, '053', '501', 'EXT',   (2012, 1,11, 11,34), (2012, 1,12, 14,00), ''),
        ( 28, '053', '501', 'PMT2',  (2012, 1,12, 14,03), (2012, 1,13, 14,20), 'rext'),
        ( 29, '053', 'test', 'PMT2', (2012, 1,13, 14,30), (2012, 1,15, 17,48), 'r501'),
        ( 30, '053', 'test', 'EXT',  (2012, 1,15, 17,58), (2012, 1,17, 11,07), 'r501'),
        ( 31, '053', 'test', 'EXT',  (2012, 1,17, 11,10), (2012, 1,18, 13,23), 'rext r501'),
        ( 32, '053', 'test', 'PMT2', (2012, 1,18, 13,26), (2012, 1,19,  9,26), 'rext r501'),
        ( 33, '018', 'test', 'PMT1', (2012, 5, 9, 15,15), (2012, 5,10, 11,13), ''),
        ( 34, '050', 'test', 'PMT1', (2012, 5,10, 11,50), (2012, 5,11, 15,03), ''),
        ( 35, '050', 'test', 'PMT1', (2012, 5,11, 15,10), (2012, 5,12, 22,45), ''),
        ( 36, '050', 'test', 'EXT',  (2012, 5,12, 22,59), (2012, 5,14,  7,00), ''),
        ( 37, '050', 'test', 'PMT2', (2012, 5,31, 14,24), (2012, 6, 4, 14,00), ''),
        ( 38, '318', 'test', 'PMT2', (2012, 6,12, 15,13), (2012, 6,18, 15,00), ''),
        ( 39, '301', 'test', 'PMT1', (2012, 7,17, 14,16), (2012, 7,18, 12,12), ''),
        ( 40, '321', 'test', 'PMT1', (2012, 7,18, 12,16), (2012, 7,19, 13,32), 'slv301'),
        ( 41, '301', 'test', 'EXT',  (2012, 7,19, 13,35), (2012, 7,23, 10,00), ''),
        ( 42, '328', 'test', 'PMT1', (2012, 7,24, 13,15), (2012, 7,28, 12,33), 'slv301'),
        ( 43, '328', 'test', 'PMT2', (2012, 7,30,  9,13), (2012, 8, 7, 14,40), 'slv301'),)

    test_all = [Tijdtest(*test) for test in tests]

    return test_all


def get_tests(id=None, hisparc=None, gps=None, trigger=None, group=None,
              note=None, subset='ALL', complement=True, part=None, unique=True):
    """ Search available tests and return those that match request

    Tests can be retrieved based on their parameters.
    The HiSPARC box number, the GPS used and the trigger of the swapped box.

    Some special cases exist;
    the pulse generator was set at a different interval (int#)
    the reference used the external trigger (rext)
    the GPS position of the reference was set incorrectly (rbgps)
    the GPS position of the swap was set incorrectly (sbgps)
    the reference used the 501 gps (r501)
    the swap was slave to master ### (slv###)

    """
    #All tests from the TijdTest Log
    test_all = test_log()

    #Select a subset
    if subset in ('ALL'):
        test_list = test_all
    elif subset in ('PMT'):
        test_list = [test for test in test_all
                     if ('PMT') in test.trigger]
    elif subset in ('EXT'):
        test_list = [test for test in test_all
                     if ('EXT') in test.trigger or
                        ('rext') in test.note]
    elif subset in ('GPS'):
        test_list = [test for test in test_all
                     if ('test') in test.gps or
                        ('r501') in test.note]
    elif subset in ('Bad'):
        test_list = [test for test in test_all
                     if ('sbgps') in test.note or
                        ('rbgps') in test.note]
    elif subset in ('SLV'):
        test_list = [test for test in test_all
                     if ('slv') in test.note]
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

    #Get a part of the class
    if part in (None,): pass
    elif part in ('id'): test_list = [test.id for test in test_list]
    elif part in ('hisparc'): test_list = [test.hisparc for test in test_list]
    elif part in ('trigger'): test_list = [test.trigger for test in test_list]
    elif part in ('gps'): test_list = [test.gps for test in test_list]
    elif part in ('group'): test_list = [test.group for test in test_list]
    elif part in ('time'): test_list = [test.time for test in test_list]
    elif part in ('start'): test_list = [test.start for test in test_list]
    elif part in ('end'): test_list = [test.end for test in test_list]
    elif part in ('note'): test_list = [test.note for test in test_list]

    if unique:
        test_list = sorted(set(test_list))

    return test_list

if __name__ in ('__main__'):
    print ("Number of tests: %s (unique: %s)" %
           (len(get_tests(subset='ALL', unique=False)),
            len(get_tests(subset='ALL', unique=True))))
    print ("Number of boxes: %s" %
           len(get_tests(part='hisparc', unique=True)))
    print ('HII:074:  %s' % ", ".join(get_tests(hisparc='074', part='group')))
    print ('GPS:test: %s' % ", ".join(get_tests(gps='test', part='group')))
    print ('TRG:EXT:  %s' % ", ".join(get_tests(trigger='EXT', part='group')))
    print ('HII:053, TRG:EXT: %s' %
           ", ".join(get_tests(hisparc='053', trigger='EXT', part='group')))
    print ('GRP:018/501/PMT2: %s' %
           ", ".join(get_tests(group='018/501/PMT2', part='group')))
    print ("GPS:test +comp: %s" %
           ", ".join(get_tests(subset='GPS', part='hisparc')))
    print ("BadGPS: %s" %
           ", ".join(get_tests(subset='Bad', part='hisparc')))
    print ("TRG:EXT +comp: %s" %
           ", ".join(get_tests(subset='EXT', part='group', complement=True)))
