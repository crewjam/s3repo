#!/usr/bin/env python
from setuptools import setup

setup(
  name="s3repo",
  version="1.0",
  package_dir={'': 'src'},
  packages=['s3repo'],
  entry_points={
    "console_scripts": [
      "s3repo = s3repo.command:Main",
    ],
  },
  requires=["boto"],
)
