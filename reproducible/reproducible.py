import os
import sys
import copy
import json
import random
import hashlib
import inspect
import warnings
import platform
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

# importing the pip freeze() command, for getting the installed package list.
try:
    from pip.commands import freeze as pip_freeze
except (ImportError, AttributeError):
    from pip._internal.commands import freeze as pip_freeze



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

    The parameters `repo_path`, `allow_dirty`, `allow_untracked`, `diff` are the
    same of the method `add_repo()`. Refer to this method for their
    documentation.

    :param cpuinfo:  if True, detailed information from the CPU is included.
                     Detailed information about the processor capabilities can
                     be important, as optimized numerical libraries will use
                     the CPU instruction sets as they are available, and
                     therefore may behave differently on different processors.
    """

    def __init__(self, repo_path='.', allow_dirty=False, allow_untracked=False,
                       diff=True, cpuinfo=True):
        self.reset(repo_path=repo_path, allow_dirty=allow_dirty,
                   allow_untracked=allow_untracked, diff=diff, cpuinfo=cpuinfo)

    def reset(self, repo_path='.', allow_dirty=False, allow_untracked=False,
                    diff=True, cpuinfo=True):
        """Reset the context data"""
        self._data = self._collect_basic_data(cpuinfo=cpuinfo)
        if repo_path is not None:
            self.add_repo(path=repo_path, allow_dirty=allow_dirty,
                          allow_untracked=allow_untracked, diff=diff)


    ## Basic Stuff

    def data(self):
        """Return the current tracked information, as a dictionary.

        This dictionary can be freely edited. Any subsequent reproducible method
        that requires a specific structure in the dictionary will recreate it.
        """
        return self._data

    def _collect_basic_data(self, cpuinfo):
        data = {'python' : {'implementation': platform.python_implementation(),
                                  'version' : platform.python_version_tuple(),
                                  'compiler': platform.python_compiler(),
                                  'branch'  : platform.python_branch(),
                                  'revision': platform.python_revision()},
                'argv'        : copy.copy(sys.argv),
                'platform'    : platform.platform(),
                # list of installed packages, in requirements form.
                'packages'    : list(pip_freeze.freeze()),
                'timestamp'   : self._timestamp(),
               }
        if cpuinfo:
            data['cpuinfo'] = get_cpu_info()
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
        self._data['random'] = {'state': random.getstate(),
                                'timestamp': self._timestamp()}


    ## User Data

    def add_data(self, key, data):
        """Add user-provided data to the tracking data.

        If you intend to export as json or yaml, the provided key and data must
        be serializable in those formats.

        :param key:   label for the data. It is recommended to use a string.
        :param data:  user-provided data.
        """
        self._data.setdefault('data', {})
        self._data['data'][key] = data
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
        self._data.setdefault('repositories', {})
        self._data['repositories'][path] = self.git_info(path, diff=diff)


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

    def add_file(self, path, category, already=False):
        """
        Compute and store the SHA256 hash of a file, as well as its modification
        time (mtime).

        :param path:        the path to the file.
        :param category:    group label for the file, for instance 'input',
                            'output', 'log', etc. Beside allowing to organize
                            the files into categories, this is also important
                            for the `already` flag.
        :param already:     if True, will not raise ValueError if the file was
                            already added *with the same group label*. In some
                            workflows, an input file is also an output file
                            later, and `reproducible` can track both state of
                            the file, as long as they are added under different
                            labels (presumably 'input' and 'output' in this
                            case). If False, the existing entry, if any, will be
                            overwritten.
        :raise ValueError:  if already is False, raise ValueError if the file
                            was already added.
        """
        if ((not already) and 'files' in self._data
            and category in self._data['files']
            and path in self._data['files'][category]):
            raise ValueError("the '{}' file '{}' is already tracked".format(
                                                                category, path))
        file_info = {'sha256': self._sha256(path),
                     'mtime': os.path.getmtime(path)}
        self._data.setdefault('files', {})
        self._data['files'].setdefault(category, {})
        self._data['files'][category][path] = file_info


    @classmethod
    def _sha256(cls, path):
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
            self._data['timestamp'] = self._timestamp()
        return json.dumps(self._data, sort_keys=True, indent=2)

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
                                  If True, the timestamp will become the date of
                                  the call to `export_json`.
        """
        if update_timestamp:
            self._data['timestamp'] = self._timestamp()
        with open(path, 'w') as f:
            json.dump(self._data, f, sort_keys=True, indent=2)
        return self._sha256(path)



    def yaml(self, update_timestamp=False):
        """Return the current tracking data, formated as YAML, as a string.

        :param update_timestamp: if True, update the timestamp of the tracked
                                 data. Default False.
        """
        if update_timestamp:
            self._data['timestamp'] = self._timestamp()
        return yaml.safe_dump(self._data, indent=2)

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
            self._data['timestamp'] = self._timestamp()
        with open(path, 'w') as f:
            yaml.safe_dump(self._data, f, indent=2)
        return self._sha256(path)

    def requirements(self):
        """Return a list of the installed packages.

        Note that if a package has been installed, changed or removed since
        the creation of the Context instance---or the import of reproducible
        when using module-level functions---this call will update the `packages`
        field in the tracked data.

        The result is a list of strings, gathered from the results of
        `pip freeze`.
        """
        self._data['packages'] = list(pip_freeze.freeze())
        list(pip_freeze.freeze()),
        return self._data['packages']


    def export_requirements(self, path, message=None, track_category=None):
        """Export the list of installed package as a requirements.txt file.

        :param path:    The filepath to save the file, e.g: `path/to/reqs.txt`
                        Note that no extension will be automatically included
        :param message: If not None, the message will be included after the
                        header and before the requirements.
        """
        data = self.data()
        req_str = '\n'.join(req for req in data['packages'])
        header = ('# Requirements generated by reproducible\n'
                  '# under {} {}, on {}\n'.format(data['python']['implementation'],
                                           '.'.join(data['python']['version']),
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
