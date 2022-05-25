# AuChAnn

[![Actions Status](https://github.com/UUDigitalHumanitieslab/auchann/workflows/Unit%20tests/badge.svg)](https://github.com/UUDigitalHumanitieslab/auchann/actions)

[pypi auchann](https://pypi.org/project/auchann)

## Getting Started

```bash
pip install auchann
```

The program can be run interactively from the console using the command `auchann`.

### Import as Library

```python
from auchann.align_words import align_words

transcript = input("Transcript: ")
correction = input("Correction: ")
alignment = align_words(transcript, correction)
print(alignment)
```

## Development

Install requirements:

```bash
pip install -r requirements.txt
```

Run from console:

```bash
python -m auchann
```

## Upload to PyPi

```bash
pip install pip-tools
python setup.py sdist
twine upload dist/*
```

## Run Tests

```bash
python -m unittest discover unit-tests/
```
