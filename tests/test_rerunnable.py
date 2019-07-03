"""Just verifying that the code runs on a simple example.

`test_rerunnable()` is arguably redundant with and superseeded by other tests,
but this is also the easiest test to write: even if you don't write any
other test this one should be present. Moreover, even if you code because
unrepeatable, at least this test will pass.

It also provides a minimal example of how to use the code.
"""
import os
import tempfile

import reproducible


here = os.path.dirname(__file__)


def test_rerunnable_module():
    """Test that the main methods work"""
    # reset
    reproducible.reset()

    reproducible.add_random_state()
    reproducible.add_repo('.', allow_dirty=True)
    reproducible.add_file(os.path.join(here, 'poem.txt'), category='text_input')
    reproducible.add_data('n', 10)

    reproducible.json()
    reproducible.yaml()
    reproducible.add_pip_packages()

    tmp_path = tempfile.gettempdir()
    reproducible.export_json(os.path.join(tmp_path, 'provdata.json'),
                             update_timestamp=True)
    os.remove(os.path.join(tmp_path, 'provdata.json'))
    reproducible.export_yaml(os.path.join(tmp_path, 'provdata.yaml'),
                             update_timestamp=True)
    os.remove(os.path.join(tmp_path, 'provdata.yaml'))
    reproducible.export_requirements(os.path.join(tmp_path, 'reqs.txt'))
    os.remove(os.path.join(tmp_path, 'reqs.txt'))

    reproducible.git_dirty('.')
    reproducible.git_info('.', diff=True)

    reproducible.data



def test_deprecated():
    """Test that the deprecated methods still work"""
    return
    reproducible.requirements()
    tmp_path = tempfile.gettempdir()
    reproducible.save_json(os.path.join(tmp_path, 'provdata.json'),
                             update_timestamp=True)
    os.remove(os.path.join(tmp_path, 'provdata.json'))
    reproducible.save_yaml(os.path.join(tmp_path, 'provdata.yaml'),
                             update_timestamp=True)
    os.remove(os.path.join(tmp_path, 'provdata.yaml'))


if __name__ == '__main__':
    test_rerunnable_module()
    test_deprecated()
