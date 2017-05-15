import subprocess

from numpy import float32, histogram, loadtxt, log10, uint32

from artist import Plot

LOCAL_STORE = '/Users/arne/Datastore/time_logs/'
TIME_LOG = '/Users/arne/Datastore/corsika_times.log'
OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'


def copy_time_logs():
    """Copy all time.log files from server

    This takes ~10 minutes to copy the files and create the file
    structure locally. Probably easier to run the following commands on
    the server.

    """
    cmd = ("rsync -qavz "
           "--include '*/' --include 'time.log' --exclude '*' "
           "adelaat@login.nikhef.nl:/data/hisparc/corsika/data/ "
           + LOCAL_STORE)
    run_cmd(cmd)


def extract_seeds_and_times():
    cmd = "grep -roE '^[0-9]+\.[0-9]+' " + LOCAL_STORE + " > " + TIME_LOG
    run_cmd(cmd)
    cmd1 = "sed -i '' 's;time_logs/;;g' " + TIME_LOG
    run_cmd(cmd1)
    cmd2 = "sed -i '' 's;/time.log:;,;g' " + TIME_LOG
    run_cmd(cmd2)
    cmd3 = "sed -i '' 's;_;,;g' " + TIME_LOG
    run_cmd(cmd3)


def run_cmd(cmd):
    result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    if not result == '':
        raise Exception('Failed cmd: ' + cmd)


def read_times():
    data = loadtxt(TIME_LOG, delimiter=',',
                   dtype={'names': ('seed1', 'seed2', 'walltime'),
                          'formats': (uint32, uint32, float32)})
    return data


def plot_times():
    plot = Plot('semilogx')
    data = read_times()
    walltimes = data['walltime'] / 60. / 60.  # To hours
    print 'Total time: %d years.' % (sum(walltimes) / 24. / 365.)
    print 'Longest job: %d hours.' % max(walltimes)
    print 'Shortest job: %d seconds.' % (min(walltimes) * 60. * 60.)
    counts, bins = histogram(log10(walltimes), bins=300)
    plot.histogram(counts, 10 ** bins, linestyle='fill=black')
    plot.add_pin_at_xy(4, max(counts), 'short', location='above left', use_arrow=False)
    plot.draw_vertical_line(4, 'gray')
    plot.add_pin_at_xy(24, max(counts), 'generic', location='above left', use_arrow=False)
    plot.draw_vertical_line(24, 'gray')
    plot.add_pin_at_xy(96, max(counts), 'long', location='above left', use_arrow=False)
    plot.draw_vertical_line(96, 'gray')
    plot.add_pin_at_xy(2000, max(counts), 'extra-long', location='above left', use_arrow=False)
    plot.draw_vertical_line(2000, 'gray')
    plot.set_ylabel(r'Count')
    plot.set_xlabel(r'Walltime [\si{\hour}]')
    plot.set_ylimits(min=0)
    plot.set_xlimits(min=3e-3, max=3e3)
    plot.save_as_pdf('shower_walltime')


if __name__ == "__main__":
    # copy_time_logs()
    # extract_seeds_and_times()
    plot_times()
