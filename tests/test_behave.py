"""Test that the library is behaving correctly"""
import os
import tempfile

import reproducible


def test_function_args():
    """Test the behavior of `reproducible.function_args()`"""
    def f1(a, b, c):
        return reproducible.function_args()

    assert f1(1, 'def', None) == {'a': 1, 'b': 'def', 'c': None}
    assert f1(True, {}, f1) == {'a': True, 'b': {}, 'c': f1}

    def f2(a, b, c=False, d=None):
        return reproducible.function_args()

    assert f2(1, 2, 3) == {'a': 1, 'b': 2, 'c': 3, 'd': None}
    assert f2(1, 2, d=3) == {'a': 1, 'b': 2, 'c': False, 'd': 3}


def test_export():
    """Test the JSON/YAML export functions"""
    tmp_path = tempfile.gettempdir()

    reproducible.export_yaml(os.path.join(tmp_path, 'file.yaml'))
    reproducible.export_json(os.path.join(tmp_path, 'file.json'))
    json_string = reproducible.json()
    yaml_string = reproducible.yaml()
    with open(os.path.join(tmp_path, 'file.yaml'), 'r') as fd:
        assert yaml_string == fd.read()
    with open(os.path.join(tmp_path, 'file.json'), 'r') as fd:
        assert json_string == fd.read()


if __name__ == "__main__":
    test_function_args()
    test_export()
