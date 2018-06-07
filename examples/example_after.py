"""A simple code producing and saving some results"""
import random
import pickle

import reproducible


def walk(n):
    """A simple random walk generator"""
    steps = [0]
    for i in range(n):
        steps.append(steps[-1] + random.choice([-1, 1]))
    return steps


if __name__ == '__main__':
    # recording repository state
    reproducible.add_repo(path='.', allow_dirty=True, diff=False)

    # recording parameters; this is not necessarily needed, as the code state
    # is recorded, but it is convenient.
    seed = 1
    random.seed(seed)
    reproducible.add_data('seed', seed)

    n = 10
    results = walk(n)
    reproducible.add_data('n', n)

    # recording the hash of the output file
    with open('results.pickle', 'wb') as f:
        pickle.dump(results, f)
    reproducible.add_file('results.pickle', 'output')

    # saving the provenance data
    reproducible.save_yaml('results_prov.yaml')
