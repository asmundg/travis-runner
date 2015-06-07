import base64
import os
import sys

import begin
from Crypto.PublicKey import RSA

KEY_SIZE = 4096


def env_privkey():
    return RSA.importKey(
        os.environ['TRAVIS_RUNNER_PRIVKEY'])


@begin.subcommand(group='crypto')
def generate():
    """Print new private key
    """
    pkey = RSA.generate(KEY_SIZE)
    sys.stdout.write('{}\n'.format(pkey.exportKey()))


@begin.subcommand(group='crypto')
def pubkey():
    """Get private key from env, print public key
    """
    sys.stdout.write(
        '{}\n'.format(env_privkey().publickey().exportKey()))


@begin.subcommand(group='crypto')
def encrypt(string):
    """Encrypt string with public key read from stdin
    """
    sys.stdout.write(
        'secure: {}\n'.format(
            base64.b64encode(
                RSA.importKey(sys.stdin.read()).encrypt(string, 0)[0])))


@begin.subcommand(group='crypto')
def decrypt(string):
    return env_privkey().decrypt(base64.b64decode(string))


@begin.start(sub_group='crypto')
def run():
    pass
