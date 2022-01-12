from setuptools import setup, findpackages

setup(
    name='auchann',
    version='0.1.0',
    packages=findpackages(include=['auchann', 'auchann.*'])
)
