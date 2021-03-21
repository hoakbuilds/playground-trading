import os

from setuptools import (
    setup, find_packages,
)

root_directory = os.path.dirname(os.path.realpath(__file__))


with open(os.path.join(root_directory, 'Requirements.txt'), 'r') as f:
    requirements = [x for x in f.readlines()]

with open(os.path.join(root_directory, 'README.md'), 'r') as f:
    long_description = f.read()

cfg = {}

with open('playground/__init__.py', 'r') as f:
    exec(f.read(), cfg)

setup(
    python_requires='>=3.6.9',
    name=cfg['__title__'],
    version=cfg['__version__'],
    author=cfg['__author__'],
    author_email=cfg['__email__'],
    description="more than a trading bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/murlokito/playground",
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'playground=playground.main:main',
        ],
    },
    install_requires=requirements,
    zip_safe=False,
    keywords=[],
    classifiers=[],
)