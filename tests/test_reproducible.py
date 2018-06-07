import os
import reproducible


here = os.path.dirname(__file__)

def test_sha256():
    context = reproducible.Context(repo_path=None)
    path = os.path.join(here, 'poem.txt')
    context.add_file(path, 'input')

    sha256 = 'bf41d9903d19d62bdae1de79e904d361fcfa6968b7cb69c7e454d5e96200b85d'
    assert context.data['files']['input'][path]['sha256'] == sha256
