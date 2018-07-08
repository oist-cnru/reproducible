import time

import reproducible


def test_repeatable():
    """Check that executions of walk with identical parameters yield the same results."""
    for path in ('.', None):
        git_data_1 = reproducible.Context(repo_path=path, allow_dirty=True).data()
        time.sleep(0.01)
        git_data_2 = reproducible.Context(repo_path=path, allow_dirty=True).data()

        timestamp_1 = git_data_1.pop('timestamp')
        timestamp_2 = git_data_2.pop('timestamp')
        assert timestamp_1 != timestamp_2
        assert git_data_1 == git_data_2

if __name__ == '__main__':
    test_repeatable()
