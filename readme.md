# The Reproducible Python Library
*Keep track of your results.*

Ever produced a result for a paper, only to realize a few months later that you
could not reproduce it? That you had no idea which version of the code, and
which parameter values were used back then?

The reproducible library, developped by the [Cognitive Neuro-Robotics
Unit](https://groups.oist.jp/cnru) at the [Okinawa Institute of Science and
Technology](http://www.oist.jp/) (OIST), aims to provide an easy way to gather and save
important information about the context in which a result was computed. This
includes details about the OS, the Python version, the time, the git commit, the
command-line arguments, hashes of input and output files, and any user provided
data.

Other Python libraries doing just that exists such as
[Recipy](https://github.com/recipy/recipy) and
[Sumatra](http://neuralensemble.org/sumatra/). And they are good. Do try them.
They each have their own design philosophy, which proved to be difficult to
interface with some of the workflows of the Cognitive Neuro-Robotics
Unit lab at OIST.

With [Reproducible](https://github.com/oist-cnru/reproducible.git) the goal was
to have a small non-intrusive library allowing precise control over the data
collected and how to output it. In particular, the goal was to have the tracking
info sitting next to—or better, directly embedded in—the result files. That
makes sending results to collaborators or packaging them for publication
straightforward.

The reproducible library is licensed under the [LGPL version
3](https://www.gnu.org/licenses/lgpl-3.0.md), to allow you to use it along-side
code that use other licenses.

The library is in beta; expect some changes. Python 3.5 or later is officially
supported, but [the code runs on 2.7 and 3.4 (but not on 3.3) as
well](https://travis-ci.org/oist-cnru/reproducible).


## Install

`pip install reproducible`


## Instant Tutorial

Say this is your code, which is fully committed using git:

```python
import random
import pickle

def walk(n):
    """A simple random walk generator"""
    steps = [0]
    for i in range(n):
        steps.append(steps[-1] + random.choice([-1, 1]))
    return steps

if __name__ == '__main__':
    random.seed(1)
    results = walk(10)
    with open('results.pickle', 'wb') as f:
        pickle.dump(results, f)
```

To add reproducible tracking:

```python
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
    # here we are okay with running our code with uncommitted changes, but
    # we record a diff of them in the tracked data.
    reproducible.add_repo(path='.', allow_dirty=True, diff=True)

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
    reproducible.add_file('results.pickle', category='output')

    # you can examine the tracked data and add or remove from it at any moment
    # by running `reproducible.data()`: it is a simple dictionary

    # saving the provenance data
    reproducible.save_yaml('results_prov.yaml')
```

See also the The [API Reference](https://reproducible.readthedocs.io/).
