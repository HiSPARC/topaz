import tables


def determine_failed_percentrage(status):
    datapath = '/Users/arne/Datastore/check_trigger/result_{status}_thresholds.h5'.format(status=status)
    with tables.open_file(datapath, 'r') as data:
        t_trigger = data.root.s501.events.col('t_trigger')
        print ('%5.2f%% failed trigger reconstructions with %s thresholds' %
               (100. * sum(t_trigger == -999) / len(t_trigger), status))

if __name__ == "__main__":
    for status in ['good', 'bad']:
        determine_failed_percentrage(status)
