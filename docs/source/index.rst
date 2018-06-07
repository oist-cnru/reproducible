Reproducible Documentation
==========================

.. toctree::

Reference
---------

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

.. autofunction:: reproducible.add_repo
.. autofunction:: reproducible.add_file
.. autofunction:: reproducible.add_data
.. autofunction:: reproducible.add_random_state

Export Functions
~~~~~~~~~~~~~~~~

.. autofunction:: reproducible.save_json
.. autofunction:: reproducible.save_yaml


Git Repository Functions
~~~~~~~~~~~~~~~~~~~~~~~~

The :py:func:`reproducible.git_info` and :py:func:`reproducible.git_dirty` can
be used to access the state of the git repository directly.

.. autofunction:: reproducible.git_info
.. autofunction:: reproducible.git_dirty
