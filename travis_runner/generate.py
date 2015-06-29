import itertools
import json
import os
import uuid

import begin
import yaml


@begin.start
def main(config='.travis.yml', destdir='.'):
    config = yaml.load(open(config))
    envs = []
    language_setup(config, envs)
    envs = itertools.chain(*[setup_matrix_env(config, env) for env in envs])
    for i, env in enumerate(envs):
        setup_system_env(env)
        setup_global_env(config, env)
        setup_addon_env(config, env)
        build_steps(config, env)
        sh_name = os.path.join(destdir, '.travis-runner-{}.sh'.format(i))
        with open(sh_name, 'w') as f:
            f.write(
                '\n'.join([
                    '{0} || (echo "Command {0} exited with code $?"; exit 1)'
                    .format(cmd) for cmd in env]))
        with open(sh_name + '.links', 'w') as f:
            f.write(json.dumps(services(config)))


def services(config):
    links = []
    pg_version = config.get('addons', {}).get('postgresql')
    mongo = 'mongodb' in config.get('services', [])
    if pg_version is not None:
        links.append(
            dict(
                name=str(uuid.uuid4()), args='-e POSTGRES_PASSWORD=pg',
                image='postgres:{}'.format(pg_version), link='postgres'))
    if mongo:
        links.append(
            dict(
                name=str(uuid.uuid4()), args='',
                image='mongo:2.6.10', link='mongodb'))

    return links


def setup_addon_env(config, env):
    if config.get('addons', {}).get('postgresql'):
        env.append('export PGHOST="$POSTGRES_PORT_5432_TCP_ADDR"')
        env.append('export PGPORT="$POSTGRES_PORT_5432_TCP_PORT"')


def listify(arg):
    """
     Given an argument that's either a string or a list of strings,
     return either a list with the string or the unmodified list.

     Useful to handle cases like env: global: foo | env: global: - foo
    """
    if isinstance(arg, list):
        return arg
    else:
        return [arg]


def apt_get(*packages):
    return ('apt-get update && apt-get install --no-install-recommends --yes'
            '  {}'.format(' '.join(packages)))


def setup_system_env(env):
    proxy = os.environ.get('http_proxy')
    if proxy is not None:
        env.insert(
            0, 'echo "Acquire::http::Proxy \\"{}\\";" > /etc/apt/apt.conf'
            .format(proxy))
        env.insert(0, 'export http_proxy={}'.format(proxy))
    env.insert(0, 'set -o errexit')
    env.insert(0, 'set -o pipefail')
    env.append(apt_get('sudo'))


def setup_global_env(config, env):
    """
     Get global env variables

     env:
       global:
         - FOO=bar
       matrix:
         - BAR=bar
         - BAR=baz
    """
    envs = config.get('env', {})
    if isinstance(envs, dict):
        for val in listify(envs.get('global', [])):
            env.append('export {}'.format(val))


def setup_matrix_env(config, env):
    """Get matrix env variables. Returns a list of env permutations.

     env:
       global:
         - FOO=bar
       matrix:
         - BAR=bar
         - BAR=baz
     or

     env:
       - BAR=bar
       - BAR=baz

     will generate permutations of the original env with the matrix
     variables:

     [[BAR=bar, <env>], [BAR=baz, <env>]]

    """
    envs = config.get('env', {})
    if isinstance(envs, dict):
        matrix = listify(envs.get('matrix', []))
    else:
        matrix = listify(envs)

    return ([env[:] + ['export {}'.format(val)] for val in matrix]
            if matrix else [env[:]])


def language_setup(config, envs):
    if config.get('language') == 'c':
        setup_c(config, envs)
    elif config.get('language') == 'go':
        setup_go(config, envs)
    elif config.get('language') == 'node_js':
        setup_node(config, envs)
    elif config.get('language') == 'python':
        setup_python(config, envs)
    else:
        envs.append([])


def setup_c(config, envs):
    for compiler in listify(config.get('compiler', ['gcc'])):
        setup = []
        envs.append(setup)
        setup.append(apt_get('clang gcc automake autoconf make scons'))
        setup.append('export CC={}'.format(compiler))


def setup_go(config, envs):
    """
     Install go dependencies

     language: go
     go:
       - "1.4"
    """
    for version in listify(config.get('go', ['1.4'])):
        setup = []
        envs.append(setup)
        setup.append(apt_get('ca-certificates', 'curl', 'git'))
        setup.append(
            'curl https://storage.googleapis.com/golang/'
            'go{0}.linux-amd64.tar.gz -o /tmp/go.tar.gz'
            .format(version))
        setup.append('tar xf /tmp/go.tar.gz -C /usr/local/')
        setup.append('export GOROOT=/usr/local/go')
        setup.append('export GOPATH=/tmp')
        setup.append('export PATH=$PATH:$GOROOT/bin')


def setup_node(config, envs):
    """
     Install node dependencies

     language: node_js
     node_js:
       - "0.12"
    """
    for version in listify(config.get('node_js', [])):
        setup = []
        envs.append(setup)
        setup.append(apt_get('ca-certificates', 'curl'))
        setup.append(
            'curl --location'
            ' https://raw.github.com/creationix/nvm/master/nvm.sh'
            ' -o /tmp/nvm.sh')
        # Disable error checking in NVM
        # (https://github.com/creationix/nvm/issues/721)
        setup.append('set +o errexit')
        setup.append('. /tmp/nvm.sh')
        setup.append('set -o errexit')
        setup.append('nvm install {}'.format(version))


def setup_python(config, envs):
    for version in listify(config.get('python', ['2.7'])):
        setup = []
        envs.append(setup)

        setup.append(
            apt_get('python-setuptools', 'python-software-properties'))
        setup.append('apt-add-repository --yes ppa:fkrull/deadsnakes')
        setup.append(apt_get('python{}-dev'.format(version)))
        setup.append('easy_install virtualenv')
        setup.append(
            'virtualenv --python python{} /tmp/virtualenv'.format(version))
        setup.append('. /tmp/virtualenv/bin/activate')


def build_steps(config, env):
    _sudo = config.get('sudo', True)
    env.append('cp -ar /src /work')
    env.append('cd /work')
    for step in ('before_install', 'install', 'before_script', 'script'):
        for command in listify(config.get(step, [])):
            if not _sudo and step in ('before_script', 'script'):
                env.append('chown -R nobody /work')
                command = 'sudo -E -u nobody env PATH=$PATH {}'.format(command)
            env.append(command)
