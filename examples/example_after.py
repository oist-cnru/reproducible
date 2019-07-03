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
    # create a reproducible.Context instance, that will hold all the
    # tracked data.
    context = reproducible.Context()

    # recording git repository state
    # here we are okay with running our code with uncommitted changes, but
    # we record a diff of the changes in the tracked data.
    context.add_repo(path='.', allow_dirty=True, diff=True)

    # recording parameters; this is not necessarily needed, as the code state
    # is recorded, but it is convenient.
    seed = 1
    random.seed(seed)
    context.add_data('seed', seed)

    # add_data return the provided value (here 10), so you can do this:
    n = reproducible.add_data('n', 10)
    results = walk(n)

    with open('results.pickle', 'wb') as f:
        pickle.dump(results, f)
    # recording the SHA1 hash of the output file
    context.add_file('results.pickle', category='output')

    # you can examine the tracked data and add or remove from it at any moment
    # with `context.data`: it is a simple dictionary. For instance, the
    # cpu info is quite detailed. Let's remove it to keep the yaml output short.
    context.data.pop('cpuinfo')

    # exporting the provenance data to disk
    context.export_yaml('results_prov.yaml')
