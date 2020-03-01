import os
import reproducible

# from test_repeatable import _scrub_cpu_info


here = os.path.dirname(__file__)

def test_sha256():
    context = reproducible.Context(cpuinfo=False)
    path = os.path.join(here, 'poem.txt')
    context.add_file(path, 'input')

    # _scrub_cpu_info(context.data)

    sha256 = 'bf41d9903d19d62bdae1de79e904d361fcfa6968b7cb69c7e454d5e96200b85d'
    assert context.data['files']['input'][path]['sha256'] == sha256

def test_data():
    assert len(reproducible.data) > 0
    reproducible.data.clear()
    assert len(reproducible.data) == 0
    reproducible.add_data('k', 10)
    assert reproducible.data == {'data': {'k': 10}}


if __name__ == '__main__':
    test_sha256()
    test_data()
