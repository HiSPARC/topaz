import os
import textwrap
import subprocess


SCRIPT_TEMPLATE = textwrap.dedent("""\
    #!/usr/bin/env bash
    umask 002
    source activate /data/hisparc/corsika_env &> /dev/null
    cd /data/hisparc/adelaat/science_park_corsika
    mkdir {seed}
    cd {seed}
    ln -s /data/hisparc/corsika/data/{seed}/corsika.h5 corsika.h5
    python ../run.py
    # To alleviate Stoomboot, make sure the job is not to short.
    sleep $[ ( $RANDOM % 60 ) + 60 ]""")



def get_script_path(seed):
    script_name = 'spa_sim_{seed}.sh'.format(seed=seed)
    script_path = os.path.join('/tmp', script_name)
    return script_path


def delete_script(seed):
    """Delete script after creating job on Stoomboot"""
    script_path = get_script_path(seed)
    os.remove(script_path)


def create_script(seed):
    """Create script as temp file to run on Stoomboot"""

    script_path = get_script_path(seed)

    with open(script_path, 'w') as script:
        script.write(SCRIPT_TEMPLATE.format(seed=seed))
    os.chmod(script_path, 0774)

    return script_path


def submit_job(seed):
    """Submit job to Stoomboot"""

    script_path = create_script(seed)

    qsub = ('qsub -q long -V -z -j oe -N spa_sim_{name} {script}'
            .format(name=seed, script=script_path))

    result = subprocess.check_output(qsub, stderr=subprocess.STDOUT,
                                     shell=True)
    if not result == '':
        logger.error('%s - Error occured: %s' % (seed, result))
        raise Exception

    delete_script(seed)


if __name__ == "__main__":
    with open('seed_list.txt', 'r') as seed_list:
        seeds = seed_list.read().split('\n')

    for seed in seeds:
        if not seed == '':
            submit_job(seed)
