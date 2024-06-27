import numpy as np
import os.path as osp
from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        content = f.read()
    return content


def find_version():
    version_file = 'medcs/__init__.py'
    with open(version_file, 'r') as f:
        exec(compile(f.read(), version_file, 'exec'))
    return locals()['__version__']


def numpy_include():
    try:
        numpy_include = np.get_include()
    except AttributeError:
        numpy_include = np.get_numpy_include()
    return numpy_include


def get_requirements(filename='requirements.txt'):
    here = osp.dirname(osp.realpath(__file__))
    with open(osp.join(here, filename), 'r') as f:
        requires = [line.replace('\n', '') for line in f.readlines()]
    return requires


setup(
    name='medcs',
    version=find_version(),
    description='MedCS',
    author='Huahui Yi',
    license='MIT',
    long_description=readme(),
    url='',
    packages=find_packages(),
    install_requires=get_requirements(),
    keywords=[
        'Multi-modal Learning', 'Multi-instance Learning',
        'Survival Prediction', 'Pytorch'
    ]
)
