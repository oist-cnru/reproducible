import time

import reproducible


def _scrub_cpu_info(data):
    """Remove data from cpu info that is not reproducible"""
    data['cpuinfo'].pop('hz_actual', None)
    data['cpuinfo'].pop('hz_actual_raw', None)
    data['cpuinfo'].pop('hz_advertised', None)
    data['cpuinfo'].pop('hz_advertised_raw', None)

def test_repeatable():
    """Check that executions of walk with identical parameters yield the same results."""
    for path in ('.', None):
        git_data_1 = reproducible.Context(cpuinfo=False).data
        #time.sleep(0.01)
        git_data_2 = reproducible.Context(cpuinfo=False).data

        timestamp_1 = git_data_1.pop('timestamp')
        timestamp_2 = git_data_2.pop('timestamp')
        #_scrub_cpu_info(git_data_1)
        #_scrub_cpu_info(git_data_2)

        assert timestamp_1 != timestamp_2
        assert git_data_1 == git_data_2

if __name__ == '__main__':
    test_repeatable()
