import contextlib
import glob
import logging
import json
import os
import shutil
import subprocess
import sys
import tempfile

import begin

from . import generate


@contextlib.contextmanager
def tempdir(debug=False):
    _dir = tempfile.mkdtemp()
    try:
        yield _dir
    finally:
        if debug:
            logging.info('Leaving tmpdir {} alone'.format(_dir))
        else:
            shutil.rmtree(_dir)


@begin.start
@begin.logging
def main(debug=False):
    failed = False

    with tempdir(debug) as _dir:
        generate.main(destdir=_dir)
        for env in glob.glob(os.path.join(_dir, '.travis-runner-*.sh')):
            links = json.load(open(env + '.links'))
            link_arg = ''
            if links:
                subprocess.check_call(
                    'docker run --name {name} {args} -d {image}'
                    .format(**links),
                    shell=True)
                link_arg = '--link {name}:{link}'.format(**links)
            try:
                subprocess.check_call(
                    'docker run {0} --rm -e http_proxy=$http_proxy'
                    ' -v $(pwd):/src'
                    ' -v {1}:/{1}'
                    ' ubuntu:precise bash -x {2}'.format(
                        link_arg, _dir, env), shell=True)
            except subprocess.CalledProcessError:
                if links:
                    subprocess.check_call(
                        'docker rm -f {name}'.format(**links), shell=True)
                    failed = True

    if failed:
        sys.exit(1)
