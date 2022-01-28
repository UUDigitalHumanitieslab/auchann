from setuptools import setup, find_packages

setup(
    name='auchann',
    version='0.1.0',
    packages=find_packages(include=['auchann', 'auchann.*']),
    install_requires=[
        'chamd',
        'editdistance',
        'numpy'
        ]
)
