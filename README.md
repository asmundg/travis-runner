# travis-runner
Local job runner for travis using docker.

This will execute jobs defined in a .travis.yml file, exiting with an
error code if anything fails.

# Dependencies

 * Docker

# Getting started

To install:

    pip install --user vex
    vex -m travis-runner pip install travis-runner

Then, in a folder containing a .travis.yml:

    vex travis-runner travis-runner

# Supported language presets

 * C (language: c)
 * Go (language: go)
 * Node (language: node_js)
 * Python (language: python)

# Supported databases

 * MongoDB (services: mongodb)
 * PostgreSQL (addons: postgresql)

# Configuration

## Python

If the TRAVIS_RUNNER_PIP_CACHE env variable is defined, this folder
will be used as a persistent pip cache for tarballs and
wheels.

# Conformance

Everything is intended to work as documented by Travis
(http://docs.travis-ci.com/). Any deviations are assumed to be bugs in
my code until proven otherwise.
