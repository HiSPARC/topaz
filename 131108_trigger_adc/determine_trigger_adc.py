import zlib

import numpy as np
import tables


def get_trace(blobs, idx):
    """Returns a trace given an index into the blobs array.

    Decompress a trace from the blobs array.

    :param idx: index into the blobs array
    :returns: array of pulseheight values

    """
    trace = zlib.decompress(blobs[idx]).split(',')
    if trace[-1] == '':
        del trace[-1]
    trace = np.array([int(x) for x in trace])
    return trace


if __name__ == '__main__':
    datapath = '/Users/arne/Datastore/2013/11/2013_11_5.h5'
    with tables.open_file(datapath, 'r') as data:
        lowest_maximums = []
        for node in data.walk_nodes('/hisparc/cluster_aarhus'):
            if node._v_name == 'events':
                lowest_max = 253
                for event in node:
                    for trace_idx in event['traces']:
                        if trace_idx != -1:
                            trace = get_trace(node._v_parent.blobs, trace_idx)
                            if max(trace) < lowest_max:
                                lowest_max = min(max(trace), lowest_max)
                                raise Exception
                lowest_maximums.append([node._v_parent._v_name, lowest_max])
                print lowest_maximums[-1]
