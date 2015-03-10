# travis-runner
Local job runner for travis using docker

# Dependencies

 #. Docker
 #. python3

# Getting started

    pip install --user vex
    vex --python python3.4 -m travis-runner python setup.py install
    vex travis-runner travis-runner

# Supported language presets

 #. Go (language: go)
 #. Node (language: node_js)
 #. Python (language: python)

# Conformance

Everything is intended to work as documented by Travis
(http://docs.travis-ci.com/). Any deviations are assumed to be bugs in
my code until proven otherwise.
