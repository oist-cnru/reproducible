"""Test that the library is behaving correctly"""
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


if __name__ == "__main__":
    test_function_args()
