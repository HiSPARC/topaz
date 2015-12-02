def nanoseconds_from_ext_timestamp(ext_timestamp):
    """Get the nanosecond part of the ext_timestamp"""

    nanoseconds = [int(ts) - ((int(ts) / int(1e9)) * int(1e9))
                   for ts in ext_timestamp]
    return nanoseconds


def timestamps_from_ext_timestamp(ext_timestamp):
    """Get the timestamp part of the ext_timestamp"""

    timestamps = [int(ts) / int(1e9) for ts in ext_timestamp]
    return timestamps
