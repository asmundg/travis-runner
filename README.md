# travis-runner
Local job runner for travis using docker

# Dependencies

 * Docker

# Getting started

    pip install --user vex
    vex -m travis-runner python setup.py install
    vex travis-runner travis-runner

# Supported language presets

 * C (language: c)
 * Go (language: go)
 * Node (language: node_js)
 * Python (language: python)

# Supported databases

 * MongoDB (services: mongodb)
 * PostgreSQL (addons: postgresql)

# Conformance

Everything is intended to work as documented by Travis
(http://docs.travis-ci.com/). Any deviations are assumed to be bugs in
my code until proven otherwise.
