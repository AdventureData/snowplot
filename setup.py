#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Micah Johnson",
    author_email='micah.johnson150@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A python package for plotting vertical profiles for analyzing snow",
    entry_points={
        'console_scripts': [
            'snowplot=snowplot.cli:main',
        ],

    },
    package_data={'snowplot':['./master.ini','./recipes.ini']},
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='snowplot',
    name='snowplot',
    packages=find_packages(include=['snowplot', 'snowplot.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/micahjohnson150/snowplot',
    version='0.1.0',
    zip_safe=False,
)
