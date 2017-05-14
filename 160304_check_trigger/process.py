import tables

from sapphire import ProcessEventsFromSourceWithTriggerOffset
from sapphire.analysis.process_events import ProcessEventsWithTriggerOffset

if __name__ == "__main__":
    with tables.open_file('/Users/arne/Datastore/check_trigger/data.h5', 'r') as source_file:
        with tables.open_file('/Users/arne/Datastore/check_trigger/result_bad_thresholds.h5', 'w') as tmp_file:
            process = ProcessEventsFromSourceWithTriggerOffset(
                source_file, tmp_file, '/s501', '/s501', progress=True)
            # These were the threshold for 501 when the mV values were
            # converted to ADC counts using the 200 baseline and 0.57
            # conversion factor.
            process.thresholds = [(227, 323)] * 4
            process.process_and_store_results()

        with tables.open_file('/Users/arne/Datastore/check_trigger/result_good_thresholds.h5', 'w') as tmp_file:
            # Use the trigger settings from the API.
            process = ProcessEventsFromSourceWithTriggerOffset(
                source_file, tmp_file, '/s501', '/s501', 501, progress=True)
            process.process_and_store_results()

    with tables.open_file('/Users/arne/Datastore/check_trigger/data.h5', 'r') as source_file:
        with tables.open_file('/Users/arne/Datastore/check_trigger/result_bad_thresholds.h5', 'w') as tmp_file:
            process = ProcessEventsFromSourceWithTriggerOffset(
                source_file, tmp_file, '/s501', '/s501', progress=True)
            # These were the threshold for 501 when the mV values were
            # converted to ADC counts using the 200 baseline and 0.57
            # conversion factor.
            process.thresholds = [(227, 323)] * 4
            process.process_and_store_results()

        with tables.open_file('/Users/arne/Datastore/check_trigger/result_good_thresholds.h5', 'w') as tmp_file:
            # Use the trigger settings from the API.
            process = ProcessEventsFromSourceWithTriggerOffset(
                source_file, tmp_file, '/s501', '/s501', 501, progress=True)
            process.process_and_store_results()

    with tables.open_file('/Users/arne/Datastore/check_trigger/data_502_1.h5', 'r') as source_file:
        process = ProcessEventsWithTriggerOffset(source_file, '/s502', progress=True)
        # These were the default thresholds used before different thresholds
        # were supported.
        process.thresholds = [(253, 323)] * 4
        timings = process.process_traces()
        print 100. * sum(timings[:, 4] == -999) / len(timings),
        print '% trigger reconstructions failed'

        process = ProcessEventsWithTriggerOffset(source_file, '/s502', progress=True)
        # These were the thresholds for 502 when values of 0 mV were
        # converted to 0 ADC counts.
        process.thresholds = [(0, 0)] * 4
        timings = process.process_traces()
        print 100. * sum(timings[:, 4] == -999) / len(timings),
        print '% trigger reconstructions failed'

        process = ProcessEventsWithTriggerOffset(source_file, '/s502', progress=True)
        # These are the correct thresholds for 502 by converting values of 0 mV
        # 200 ADC counts.
        process.thresholds = [(200, 200)] * 4
        timings = process.process_traces()
        print 100. * sum(timings[:, 4] == -999) / len(timings),
        print '% trigger reconstructions failed'

    with tables.open_file('/Users/arne/Datastore/check_trigger/data_502_2.h5', 'r') as source_file:
        process = ProcessEventsWithTriggerOffset(source_file, '/s502', progress=True)
        # These were the default thresholds used before different thresholds
        # were supported.
        process.thresholds = [(253, 323)] * 4
        timings = process.process_traces()
        print 100. * sum(timings[:, 4] == -999) / len(timings),
        print '% trigger reconstructions failed'

        process = ProcessEventsWithTriggerOffset(source_file, '/s502', progress=True)
        # These were the thresholds for 502 when values of 0 mV were
        # converted to 0 ADC counts.
        process.thresholds = [(0, 0)] * 4
        timings = process.process_traces()
        print 100. * sum(timings[:, 4] == -999) / len(timings),
        print '% trigger reconstructions failed'

        process = ProcessEventsWithTriggerOffset(source_file, '/s502', progress=True)
        # These are the correct thresholds for 502 by converting values of 0 mV
        # 200 ADC counts.
        process.thresholds = [(200, 200)] * 4
        timings = process.process_traces()
        print 100. * sum(timings[:, 4] == -999) / len(timings),
        print '% trigger reconstructions failed'
