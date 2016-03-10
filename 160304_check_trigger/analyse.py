import tables


if __name__ == "__main__":
    with tables.open_file('result_bad_thresholds.h5', 'r') as data:
        t_trigger = data.root.s501.events.col('t_trigger')
        print ('%5.2f%% failed trigger reconstructions with bad thresholds' %
               (100. * sum(t_trigger == -999) / len(t_trigger)))

    with tables.open_file('result_good_thresholds.h5', 'r') as data:
        t_trigger = data.root.s501.events.col('t_trigger')
        print ('%5.2f%% failed trigger reconstructions with good thresholds' %
               (100. * sum(t_trigger == -999) / len(t_trigger)))
