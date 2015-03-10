import json
import os
import uuid

import begin
import yaml


@begin.start
def main(config='.travis.yml'):
    config = yaml.load(open(os.path.join(config)))
    envs = []
    language_setup(config, envs)
    for i, env in enumerate(envs):
        setup_system_env(env)
        setup_script_env(config, env)
        setup_addon_env(config, env)
        build_steps(config, env)
        sh_name = '.travis-runner-{}.sh'.format(i)
        with open(sh_name, 'w') as f:
            f.write('\n'.join(env))
        with open(sh_name + '.links', 'w') as f:
            f.write(json.dumps(services(config)))


def services(config):
    pg_version = config.get('addons', {}).get('postgresql')
    if pg_version is not None:
        name = str(uuid.uuid4())
        return dict(
            name=name, args='-e POSTGRES_PASSWORD=pg',
            image='postgres:{}'.format(pg_version), link='postgres')
    else:
        return dict()


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


def setup_system_env(env):
    proxy = os.environ.get('http_proxy')
    if proxy is not None:
        env.insert(
            0, 'echo "Acquire::http::Proxy \\"{}\\";" > /etc/apt/apt.conf'
            .format(proxy))
        env.insert(0, 'export http_proxy={}'.format(proxy))
    env.insert(0, 'set -o pipefail')


def setup_script_env(config, env):
    """
     Get global env variables

     env:
       global:
         - FOO=bar
    """
    for val in listify(config.get('env', {}).get('global', [])):
        env.append('export {}'.format(val))


def language_setup(config, envs):
    if config.get('language') == 'go':
        setup_go(config, envs)
    elif config.get('language') == 'node_js':
        setup_node(config, envs)
    elif config.get('language') == 'python':
        setup_python(config, envs)
    else:
        envs.append([])


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
        setup.append('apt-get update')
        setup.append('apt-get install --no-install-recommends --yes'
                     ' ca-certificates curl git')
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
        setup.append('apt-get update')
        setup.append('apt-get install --no-install-recommends --yes'
                     ' ca-certificates curl')
        setup.append(
            'curl --location --insecure'
            ' https://raw.github.com/creationix/nvm/master/nvm.sh'
            ' -o /tmp/nvm.sh')
        setup.append('. /tmp/nvm.sh')
        setup.append('nvm install {}'.format(version))


def setup_python(config, envs):
    setup = []
    envs.append(setup)
    setup.append('apt-get update')
    setup.append(
        'apt-get install --no-install-recommends --yes'
        ' python python-dev python-setuptools')
    setup.append('easy_install pip')


def build_steps(config, env):
    _sudo = config.get('sudo', True)
    if not _sudo:
        env.append('apt-get update')
        env.append('apt-get install --no-install-recommends --yes sudo')
    env.append('cp -ar /src /work')
    env.append('cd /work')
    for step in ('before_install', 'install', 'before_script', 'script'):
        for command in listify(config.get(step, [])):
            if not _sudo and step in ('before_script', 'script'):
                env.append('chown -R nobody /work')
                command = 'sudo -E -u nobody env PATH=$PATH {}'.format(command)
            env.append(command)
