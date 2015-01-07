def nanoseconds_from_ext_timestamp(ext_timestamp):
    """ Get the nanosecond part of the ext_timestamp

    """
    nanoseconds = [ts - (ts / int(1e9) * int(1e9)) for ts in ext_timestamp]

    return nanoseconds


def timestamps_from_ext_timestamp(ext_timestamp):
    """ Get the timestamp part of the ext_timestamp

    """
    timestamps = [ts / int(1e9) for ts in ext_timestamp]

    return timestamps


if __name__ == '__main__':
    print 'Done'
