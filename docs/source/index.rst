Reproducible Documentation
==========================

.. toctree::

Reference
---------

.. autoclass:: reproducible.Context


Tracking Functions
~~~~~~~~~~~~~~~~~~

These functions can be used to track specific aspect of the computation. The
tracking data will always include:

* details about the OS
* details about the CPU
* details about the Python (version, implementation)
* the command-line arguments (content of sys.argv)
* the list of installed packages (we recommend to use virtual environments to
  avoid unnecessary packages here)
* the timestamp (of the import of the reproducible library)

.. autofunction:: reproducible.Context.add_repo
.. autofunction:: reproducible.Context.add_data
.. autofunction:: reproducible.Context.add_random_state
.. autofunction:: reproducible.Context.add_file
.. autofunction:: reproducible.Context.untrack_file
.. autofunction:: reproducible.Context.find_editable_repos
.. autofunction:: reproducible.Context.add_editable_repos
.. autofunction:: reproducible.Context.add_pip_packages


Export Functions
~~~~~~~~~~~~~~~~

All export function exists in two flavor. Those that export to the disk, and
those that return their output.

.. autofunction:: reproducible.Context.export_json
.. autofunction:: reproducible.Context.export_yaml
.. autofunction:: reproducible.Context.export_requirements

.. autofunction:: reproducible.Context.json
.. autofunction:: reproducible.Context.yaml
.. autofunction:: reproducible.Context.requirements


Git Repository Functions
~~~~~~~~~~~~~~~~~~~~~~~~

The :py:func:`reproducible.git_info` and :py:func:`reproducible.git_dirty` can
be used to access the state of the git repository directly.

.. autofunction:: reproducible.Context.git_info
.. autofunction:: reproducible.Context.git_dirty


Misc Functions
~~~~~~~~~~~~~~

.. autofunction:: reproducible.Context.sha256
.. autofunction:: reproducible.Context.function_args


Deprecated Functions
~~~~~~~~~~~~~~~~~~~~

Those function are likely to get removed in one of the next release.

.. autofunction:: reproducible.Context.save_json
.. autofunction:: reproducible.Context.save_yaml
.. autofunction:: reproducible.Context.requirements
