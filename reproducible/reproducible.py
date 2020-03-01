import os
import re
import sys
import copy
import json
import random
import hashlib
import inspect
import warnings
import platform
import subprocess
from datetime import datetime

# GitPython
import git

# py-cpuinfo, used for getting CPU specific capabilities
from cpuinfo import get_cpu_info

# is PyYAML installed?
try:
    import yaml
    yaml_available = True
except ImportError:
    yaml_available = False


class RepositoryNotFound(Exception):
    """Raised when a repository is not found."""
    pass


class RepositoryDirty(Exception):
    """Raised when a repository is dirty either because of uncommited files
    or untracked changes."""
    pass


class Context:
    """The `Context` class gathers the provenance data, some automatically
    (e.g. OS, Python version, git commit) and some user-provided.

    The data being tracked can be freely accessed and edited through the
    `.data` attribute. Any subsequent reproducible method that requires a
    specific structure in the dictionary will recreate it.

    :param cpuinfo:  if True, detailed information from the CPU is included.
                     Detailed information about the processor capabilities can
                     be important, as optimized numerical libraries will use
                     the CPU instruction sets as they are available, and
                     therefore may behave differently on different processors.
    """

    def __init__(self, cpuinfo=True, pip_packages=False):
        self.collect_cpuinfo      = cpuinfo
        self.collect_pip_packages = pip_packages
        self.reset()

    def reset(self):
        """Reset the context data"""
        self.data = self._collect_basic_data(cpuinfo=self.collect_cpuinfo,
                        pip_packages=self.collect_pip_packages)

    ## Basic Stuff

    def _collect_basic_data(self, cpuinfo=True, pip_packages=True):
        data = {'python' : {'implementation': platform.python_implementation(),
                                  'version' : platform.python_version_tuple(),
                                  'compiler': platform.python_compiler(),
                                  'branch'  : platform.python_branch(),
                                  'revision': platform.python_revision()},
                'argv'        : copy.copy(sys.argv),
                'platform'    : platform.platform(),
                # list of installed packages, in requirements form.
                'packages'    : None,
                'timestamp'   : self._timestamp(),
               }
        if cpuinfo:
            data['cpuinfo'] = get_cpu_info()
        if pip_packages:
            data['packages'] = self._pip_freeze()
        return data

    @classmethod
    def _timestamp(cls):
        return datetime.utcnow().isoformat()+'Z'  # Z stands for UTC


    ## Function Arguments

    def function_args(self):
        """Return a function's arguments value from inside the function.

        The function must be called from inside the function to return the
        arguments from. The arguments' value will be returned as a name -> value
        dictionary. No difference is made between positional and provided-or-not
        keyword arguments. Default values of non-provided keyword arguments are
        included in the dictionary.

        Note that this function does not add any information to the tracked
        context data. Use `add_data()` with the return of this function to do
        that.
        """
        frame = inspect.stack(context=1)[1][0]
        return inspect.getargvalues(frame).locals


    ## Get Random State

    def add_random_state(self):
        """Record the current random state.

        The random state is different from the seed used in a `random.seed()`
        call. However, it can be used in the same way to produce reproducible
        random sequences, using the `random.setstate()` method.

        `record_random_state` should be called just after setting the seed, and
        before any use of the random draw functions. Note that you can also
        use the current time to set the seed using `random.seed()` without an
        argument, and still record the random state right after.

        Only the random state from the `random` module is recorded here, along
        with a timestamp of the recording time. If you wish to record the
        random state of external libraries such as `numpy`, you should use the
        `record_data()` method, and provide either the seed used or the
        result of the `numpy.random.get_state()`.
        """
        self.data['random'] = {'state': random.getstate(),
                                'timestamp': self._timestamp()}


    ## User Data

    def add_data(self, key, data):
        """Add user-provided data to the tracking data.

        If you intend to export as json or yaml, the provided key and data must
        be serializable in those formats.

        :param key:   label for the data. It is recommended to use a string.
        :param data:  user-provided data.
        """
        self.data.setdefault('data', {})
        self.data['data'][key] = data
        return data


    ## Version Control Repositories and Git methods

    def add_repo(self, path='.', allow_dirty=False, allow_untracked=False,
                       diff=True):
        """Add a version control repository to the tracking data. Only git is
        supported at the moment.

        Multiple repository can be tracked, each one will be identified by their
        path. Adding a repository twice will result in duplication of tracking
        data if the path strings are different.

        :param path:         the path to the repository. If a repository is not
                             found there,
        :param allow_dirty:  if False, will exit with an error if the git
                             repository is dirty or absent.
        :param diff:         if True and uncommited changes are present in the
                             repository, the diff will be recorded in a
                             patchable form. Patch diffs of binary file can
                             grow to large sizes.

        :raise FileNotFoundError:  if the path does not exist.
        :raise RepositoryNotFound: if no repository was found.
        """
        if (not allow_dirty) and self.git_dirty(path, allow_untracked=allow_untracked):
            raise RepositoryDirty("Repository '{}' is in a dirty state".format(path))
        self.data.setdefault('repositories', {})
        self.data['repositories'][path] = self.git_info(path, diff=diff)


    @classmethod
    def git_info(cls, path, diff=True):
        """
        Retrieve data from the git repository.

        This method can be used as a stand-alone, to access the git information
        directly. To add the git information to the tracked data, the `add_repo`
        method should be used.

        :param diff:         if True and uncommited changes are present in the
                             repository, the diff will be recorded in a
                             patchable form.
        :raise FileNotFoundError:  if the path does not exist.
        :raise RepositoryNotFound: if no repository was found.
        """
        repo = cls._get_repo(path)
        patch = None
        if diff and repo.is_dirty(untracked_files=False):
            t = repo.head.commit.tree
            patch = repo.git.diff(t, patch=True)

        git_version = git.cmd.Git(path).version()

        return {'hash': repo.head.object.hexsha, 'dirty': repo.is_dirty(),
                'version': git_version, 'diff': patch}

    @classmethod
    def git_dirty(cls, path, allow_untracked=False):
        """
        Return True if the repository is dirty.

        A repository is dirty if it has uncommitted changes or untracked files.
        This method can be used as a stand-alone, to access the git information
        directly. To add the git information to the tracked data, the `add_repo`
        method should be used.


        :param allow_untracked:   if False, any untracked file makes the
                                  repository dirty. Else, only uncommited
                                  changes to tracked files are considered.
        :raise FileNotFoundError:  if the path does not exist.
        :raise RepositoryNotFound: if no repository was found.
        """
        return cls._get_repo(path).is_dirty(untracked_files=not allow_untracked)

    @classmethod
    def _get_repo(cls, path, search_parent_directories=True):
        """Get the git repository

        :param path: the path of the repository, or one of its subdirectory or
                     file (if `search_parent_directories` is `True`).
        :raise FileNotFoundError:  if the path does not exist.
        :raise RepositoryNotFound: if no repository was found.
        """
        if not os.path.exists(path):
            raise FileNotFoundError("'{}' not found".format(path))
        try: # are we in a git repository?
            return git.Repo(path,
                            search_parent_directories=search_parent_directories)
        except git.InvalidGitRepositoryError: # not in a git repo
            raise RepositoryNotFound("git repository not found "
                                     "at '{}'".format(path))


    ## Input & Output files

    def add_file(self, path, category='', already=True):
        """
        Compute and store the SHA256 hash of a file, as well as its modification
        time (mtime).

        :param path:        the path to the file.
        :param category:    group label for the file, for instance 'input',
                            'output', 'log', etc. Beside allowing to organize
                            the files into categories, this is also important
                            when the `already` flag is `True`.
        :param already:     if `True`, will not raise `ValueError` if the file
                            was already added *with the same group label*. In
                            some workflows, an input file is also an output
                            file later, and `reproducible` can track both state
                            of the file, as long as they are added under
                            different categories (presumably 'input' and
                            'output' in this case). If `False`, the existing
                            entry, if any, will be overwritten.
        :return:            The computed sha256 of the file.
        :raise ValueError:  if `already` is False and the file was previously
                            added (same string path), raise ValueError.
                            Note that no normalization is done on the path when
                            checking for existence, so a file can be added
                            multiple times with different, albeit equivalent,
                            paths.
        """
        path = os.path.normpath(path)
        if ((not already) and 'files' in self.data
            and category in self.data['files']
            and path in self.data['files'][category]):
            raise ValueError("the '{}' file '{}' is already tracked".format(
                                                                category, path))
        file_info = {'sha256': self.sha256(path),
                     'mtime': os.path.getmtime(path)}
        self.data.setdefault('files', {})
        self.data['files'].setdefault(category, {})
        self.data['files'][category][path] = file_info

        return file_info['sha256']

    def untrack_file(self, path, category='', notfound_ok=False):
        """
        Untrack a tracked file, i.e. undo a `add_file` invocation.

        :param path:        the path to the file, the same that was given when
                            `add_file` was invoked.
        :param category:    category of the file that was given when adding it.
        :param notfound_ok: if `True`, will not raise `ValueError` if the file
                            was not present in the file trackeds by
                            reproducible.
        :raise ValueError:  if `notfound_ok` is False and the file was not
                            already tracked.
        """
        path = os.path.normpath(path)
        notfound = False
        try:
            self.data['files'][category].pop(path)
        except KeyError:
            if not notfound_ok:
                raise ValueError(('the `{}` file was not found as tracked in '
                                  'category {}.').format(path, category))

    @classmethod
    def sha256(cls, path):
        """Compute the SHA256 hash of a file"""
        if not os.path.isfile(path):
            raise FileNotFoundError('file {} was not found'.format(path))
        hash_sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            # reading incrementally, in case it does not fit in memory.
            for block in iter(lambda: f.read(4096), b""):
                hash_sha256.update(block)
        return hash_sha256.hexdigest()


    ## Export functions

    def json(self, update_timestamp=False):
        """Return the current tracking data, formated as JSON, as a string.

        :param update_timestamp: if True, update the timestamp of the tracked
                                 data. Default False.
        """
        if update_timestamp:
            self.data['timestamp'] = self._timestamp()
        return json.dumps(self.data, sort_keys=True, indent=2)

    def export_json(self, path, update_timestamp=False):
        """Export the tracked data as a JSON file

        Will raise error if some of the data is not JSON serializable. This
        method will return the SHA256 hexadecimal string of the saved file.

        :param path:              Path to the file to save the JSON data to.
                                  If the file exists, it will be overwritten.
        :param update_timestamp:  The global timestamp of the tracked data, is
                                  the time of the creation of the Context
                                  instance, which happens at importing time,
                                  if using the module-level functions.
                                  If True, the timestamp will become the date
                                  of the call to `export_json`.
        """
        if update_timestamp:
            self.data['timestamp'] = self._timestamp()
        with open(path, 'w') as f:
            json.dump(self.data, f, sort_keys=True, indent=2)
        return self.sha256(path)



    def yaml(self, update_timestamp=False):
        """Return the current tracking data, formated as YAML, as a string.

        :param update_timestamp: if True, update the timestamp of the tracked
                                 data. Default False.
        """
        if update_timestamp:
            self.data['timestamp'] = self._timestamp()
        return yaml.safe_dump(self.data, indent=2, allow_unicode=True)

    def export_yaml(self, path=None, update_timestamp=False):
        """Export the tracked data as a YAML file

        Will raise error if some of the data is not YAML serializable. This
        method will return the SHA256 hexadecimal string of the saved file.

        :param path:              Path to the file to save the YAML data to.
                                  If the file exists, it will be overwritten.
        :param update_timestamp:  The global timestamp of the tracked data, is
                                  the time of the creation of the Context
                                  instance, which happens at importing time,
                                  if using the module-level functions.
                                  If True, the timestamp will become the date of
                                  the call to `export_yaml`.
        :raise ImportError:  if the `yaml` module cannot be imported.
        """
        if not yaml_available:
            raise ImportError('PyYAML does not seem present or importable.')
        if update_timestamp:
            self.data['timestamp'] = self._timestamp()
        with open(path, 'w') as f:
            yaml.safe_dump(self.data, f, indent=2, allow_unicode=True)
        return self.sha256(path)


    ## Packages

    # TODO: support conda

    def _pip_freeze(self):
        output =  subprocess.check_output(['pip', 'freeze', '-qq'])
        return output.decode().split('\n')[:-1]

    def add_pip_packages(self):
        """Gather and add the list of installed packages to the tracked data.

        :return:  the packages, as a list of strings.

        This function calls `pip freeze`, which may be slow or absent, and this
        may be undesirable in some environment. It must be called manually.
        Note that `pip freeze` may report an incomplete or incorrect list.
        """
        self.data['packages'] = self._pip_freeze()
        return self.data['packages']


    def find_editable_repos(self):
        """Find editable repositories in the list of installed packages.

        :return:  a list of (name, version, path) for each of the editable
                  repository found.
        :note:    this function is considered brittle, as it relies on the
                  text output of the `pip freeze` command.
        """
        requirements = self.add_pip_packages()
        editables = []
        for i, r in enumerate(requirements):
            if r.startswith('-e'):
                desc = requirements[i - 1]
                if desc.startswith('# '):
                    reg_exp = '(.*)\\((?P<name>.+)\\=\\=(?P<version>.+)\\)'
                    m = re.fullmatch(reg_exp, desc)
                    assert m is not None
                    name, version = m.group('name'), m.group('version')
                    editables.append((name, version, r[3:]))
        return editables

    def add_editable_repos(self, allow_dirty=True, verbose=False):
        """Track all editable repository found in the list of installed packages.

        Invokes `add_repo()` on each repository found.
        """
        for editable in self.find_editable_repos():
            name, version, path = editable
            if verbose:
                print('adding editable repo {} ({})'.format(name, path))
            self.add_repo(path, allow_dirty=allow_dirty)

    def requirements(self):
        """Return a list of the installed packages.

        Note that if a package has been installed, changed or removed since
        the creation of the Context instance---or the import of reproducible
        when using module-level functions---this call will update the `packages`
        field in the tracked data.

        The result is a list of strings, gathered from the results of
        `pip freeze`.
        """
        warnings.warn('`requirements` has been renamed `add_pip_packages`.'
                      ' It will be removed in a future version',
                      DeprecationWarning)
        return self.add_pip_packages()

    def export_requirements(self, path, message=None):
        """Export the list of installed package as a requirements.txt file.

        :param path:    The filepath to save the file, e.g: `path/to/reqs.txt`
                        Note that no extension will be automatically included
        :param message: If not None, the message will be included after the
                        header and before the requirements.
        """
        if self.data['packages'] is None:
            self.add_pip_packages()
        req_str = '\n'.join(req for req in self.data['packages'])
        header = ('# Requirements generated by reproducible\n'
                  '# under {} {}, on {}\n'.format(self.data['python']['implementation'],
                                           '.'.join(self.data['python']['version']),
                                           self._timestamp()))
        if message is None:
            message = ''
        else:
            message = '{}\n'.format(message)

        req_str = '{}\n{}{}\n'.format(header, message, req_str)
        with open(path, 'w') as f:
            f.write(req_str)



    ## Deprecated Functions

    def save_yaml(self, *args, **kwargs):
        warnings.warn('`save_yaml` has been renamed `export_yaml`. It will be '
                      'removed in a future version', DeprecationWarning)
        return self.export_yaml(*args, **kwargs)

    def save_json(self, *args, **kwargs):
        warnings.warn('`save_json` has been renamed `export_json`. It will be '
                      'removed in a future version', DeprecationWarning)
        return self.export_json(*args, **kwargs)
