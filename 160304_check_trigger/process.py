import tables

from sapphire import ProcessEventsFromSourceWithTriggerOffset


if __name__ == "__main__":
    with tables.open_file('data.h5', 'r') as source_file:
        with tables.open_file('result_bad_thresholds.h5', 'w') as tmp_file:
            process = ProcessEventsFromSourceWithTriggerOffset(
                source_file, tmp_file, '/s501', '/s501', progress=True)
            # These were the threshold for 501 when the mV values were
            # converted to ADC counts using the 200 baseline and 0.57
            # conversion factor.
            process.thresholds = [(227, 323)] * 4
            process.process_and_store_results()

        with tables.open_file('result_good_thresholds.h5', 'w') as tmp_file:
            # Use the trigger settings from the API.
            process = ProcessEventsFromSourceWithTriggerOffset(
                source_file, tmp_file, '/s501', '/s501', 501, progress=True)
            process.process_and_store_results()
