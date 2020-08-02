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

With [reproducible](https://github.com/oist-cnru/reproducible.git) the goal was
to have a small non-intrusive library allowing precise control over the data
collected and how to output it. In particular, the goal was to have the tracking
info sitting next to—or better, directly embedded in—the result files. That
makes sending results to collaborators or packaging them for publication
straightforward.

The reproducible library is licensed under the [LGPL version
3](https://www.gnu.org/licenses/lgpl-3.0.md), to allow you to use it along-side
code that use other licenses.

The library is in beta; expect some changes. Python 3.5 or later is officially
supported, but for the time being, [the code runs on 2.7 as
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
```

This is the resulting yaml file output containing the tracking data:
```yaml
argv: [example_after.py]
data: {n: 10, seed: 1}
files:
  output:
    results.pickle: {mtime: 1531381834.0666547, sha256: 395d8846640c012e3e5c642e7737173a1a74120275b37fa2ded13a211df3264e}
packages: [gitdb2==2.0.3, GitPython==2.1.10, pip==10.0.1, py-cpuinfo==4.0.0, PyYAML==4.2b4,
  reproducible==0.1.2, setuptools==39.0.1, smmap2==2.0.3]
platform: Darwin-17.6.0-x86_64-i386-64bit
python:
  branch: ''
  compiler: Clang 9.1.0 (clang-902.0.39.2)
  implementation: CPython
  revision: ''
  version: ['3', '7', '0']
repositories:
  .: {diff: null, dirty: false, hash: 88c1de4ba5fb5cb2564b60245f26d3226ecb20c9, version: git
      version 2.18.0}
timestamp: ['2018-07-12T07:50:34.033829Z']
```

See also the The [API Reference](https://reproducible.readthedocs.io/).

## Roadmap

- Retrieve GPU information.
- More configurability.
- Optionally capture input, output (`sys.stderr`, `sys.stdout`).
- Easy disabling/reenabling of reproducible
- optional SHA256 in the filename of external files

## Changelog

**version 0.4.0**, *20190703*
- new functions `sha256()`, `untrack_file()`, `find_editable_repos()`, `add_editable_repos()`.
- fix tests.

**version 0.3.0**, *20190703*
This version introduces API and logic-breaking changes.
- `add_file()` overwrites by default now, and category is now an optional argument.
- `context.data()` becomes `context.data`.
- `Context(repo_path='.', allow_dirty=False, allow_untracked=False, diff=True, cpuinfo=True)`
  becomes `Context(cpuinfo=True, pip_packages=True)`: `add_repo()` needs to be called
  explicitly now, and pip_packages queries can be made optional.
- `reset()` does not accept any arguments anymore; remembers `__init__()` argument values instead.
- fixed missing `reproducible.add_pip_packages()`.

**version 0.2.4**, *20170809*
- hotfix for Python 2.7---because I am stupid.

**version 0.2.3**, *20170809*
- add `json()`, `yaml()` and `requirements()` function to access the result
  of export functions programmatically.
- YAML output is now generated using `yaml.safe_dump` rather than `yaml.dump`.
  Leads to safer and simpler output.

**version 0.2.2**, *20170717*
- fix for deprecated `save_yaml()`, `save_json()` functions.

**version 0.2.1**, *20170717*
- add readme, license to pypi package.

**version 0.2.0**, *20170717*
- renamed `save_json()` and `save_yaml()` as `export_json()` and
  `export_yaml()`. The old name remain for now with a deprecation warning.
- `Context` instances for more flexible, non-module level, behavior, much like
  the `Random` instances of the standard `random` module.
- `reproducible.function_args()` function to retrieve arguments from inside a
  function.
- `reproducible.reset()` function for clearing tracked data.
- `reproducible.export_requirements()` to create requirements files from the
  retrieved list of installed packages.
- Fix import of the freeze command from the `pip` package.
- Updated readme: yaml output of the example, roadmap, changlog.

**version 0.1.2**, *20170611*
- Various bug fixes.
- The `save_json()` and `save_yaml()` functions now return the SHA256 hash of the file they produce.

**version 0.1.1**, *20170608*
- `reproducible.data()` function to access and modify the collected data.
- more unit tests

**version 0.1.0**, *20170607*
- first version: `add_repo()`, `add_file()`, `add_data()`, `add_random_state()`, `git_info()`, `git_dirty()`, `save_json()`, `save_yaml()` functions.
