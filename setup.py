"""Setup script

For details: https://packaging.python.org/en/latest/distributing.html
"""
import os
import setuptools


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'readme.md'), 'r') as fd:
    long_description = fd.read()


setuptools.setup(
    name='reproducible',
    version='0.4.0',

    description='Reproducible library',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/oist-cnru/reproducible',

    author='Fabien C. Y. Benureau',
    author_email='fabien@benureau.com',

    license='BSD',

    keywords='replicable reproducible research',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',

        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Testing',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # where is our code
    packages=['reproducible'],

    # include readme and license file.
    package_data={'': ['readme.md', 'license.md']},
    data_files=[('.',['readme.md', 'license.md'])],
    include_package_data=True,

    # required dependencies
    install_requires=['gitpython', 'pyyaml', 'py-cpuinfo<5.0.0'],

    # you can install extras_require with
    # $ pip install -e .[test]
    extras_require={'tests': ['pytest', 'pytest-cov'],
                    'docs' : ['sphinx', 'sphinx-rtd-theme']},
)
