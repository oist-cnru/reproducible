# The Reproducible Python Library
*Keep track of your results.*

Ever produced a result for a paper, only to realize a few months later that you
could not reproduce it? That you had no idea which version of the code, and
which parameter values were used back then?

The reproducible library, developped by the [Cognitive Neuro-Robotics
Unit](https://groups.oist.jp/cnru) at the [Okinawa Institute of Science and
Technology (OIST)](http://www.oist.jp/), aims to provide an easy way to gather and save
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
    # recording git repository state
    # here we are okay with running our code with uncommitted changes, but
    # we record a diff of the changes in the tracked data.
    reproducible.add_repo(path='.', allow_dirty=True, diff=True)

    # recording parameters; this is not necessarily needed, as the code state
    # is recorded, but it is convenient.
    seed = 1
    random.seed(seed)
    reproducible.add_data('seed', seed)

    # add_data return the provided value (here 10), so you can do this:
    n = reproducible.add_data('n', 10)
    results = walk(n)

    with open('results.pickle', 'wb') as f:
        pickle.dump(results, f)
    # recording the SHA1 hash of the output file
    reproducible.add_file('results.pickle', category='output')

    # you can examine the tracked data and add or remove from it at any moment
    # with `reproducible.data()`: it is a simple dictionary. For instance, the
    # cpu info is quite detailed. Let's remove it to keep the yaml output short.
    reproducible.data().pop('cpuinfo')

    # exporting the provenance data to disk
    reproducible.save_yaml('results_prov.yaml')
```

This is the resulting yaml file output containing the tracking data:
```
argv: [example_after.py]
data: {n: 10, seed: 1}
files:
  output:
    results.pickle: {mtime: 1531378526.1395743, sha256: 395d8846640c012e3e5c642e7737173a1a74120275b37fa2ded13a211df3264e}
packages: [gitdb2==2.0.3, GitPython==2.1.10, pip==10.0.1, py-cpuinfo==4.0.0, PyYAML==4.2b4,
  reproducible==0.1.2, setuptools==39.0.1, smmap2==2.0.3]
platform: Darwin-17.6.0-x86_64-i386-64bit
python:
  branch: ''
  compiler: Clang 9.1.0 (clang-902.0.39.2)
  implementation: CPython
  revision: ''
  version: !!python/tuple ['3', '7', '0']
repositories:
  .: {diff: null, dirty: false, hash: a4b02b7b376a39e7d32eae12771bf69a0631e727, version: git
      version 2.18.0}
timestamp: !!python/tuple ['2018-07-12T06:55:26.107863Z']
```

See also the The [API Reference](https://reproducible.readthedocs.io/).
