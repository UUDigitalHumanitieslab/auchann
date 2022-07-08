from setuptools import setup, find_packages

with open('README.md') as file:
    long_description = file.read()

setup(
    name='auchann',
    version='0.1.1',
    packages=find_packages(include=['auchann', 'auchann.*']),
    package_data={'auchann': ['py.typed']},
    description=('The AuChAnn (Automatic CHAT Annotation) package can generate CHAT annotations based on a transcript-correction pairs of utterances.'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='BSD-3 Clause',
    author='Digital Humanities Lab, Utrecht University',
    author_email='digitalhumanities@uu.nl',
    url='https://github.com/UUDigitalHumanitieslab/auchann',
    install_requires=[
        'chamd>=0.5.8',
        'editdistance',
        'pyyaml-include',
        'sastadev'
    ],
    python_requires='>=3.7',
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'auchann = auchann.__main__:main'
        ]
    }
)
