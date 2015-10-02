# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(name='travis-runner',
      version='0.4.3',
      description='Local job runner for travis using docker',
      url='https://github.com/asmundg/travis-runner',
      author='Åsmund Grammeltvedt',
      author_email='asmundg@big-oil.org',
      license='MIT license',
      install_requires=['PyYAML',
                        'begins'],
      entry_points=dict(
          console_scripts=['travis-runner=travis_runner.runner:main.start']),
      packages=find_packages(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Testing'])
