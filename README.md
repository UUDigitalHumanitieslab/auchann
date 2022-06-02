# AuChAnn

[![Actions Status](https://github.com/UUDigitalHumanitieslab/auchann/workflows/Unit%20tests/badge.svg)](https://github.com/UUDigitalHumanitieslab/auchann/actions)

[pypi auchann](https://pypi.org/project/auchann)

## Getting Started

```bash
pip install auchann
```

The program can be run interactively from the console using the command `auchann` .

## Import as Library

```python
from auchann.align_words import align_words

transcript = input("Transcript: ")
correction = input("Correction: ")
alignment = align_words(transcript, correction)
print(alignment)
```

### Settings

```python
from auchann.align_words import align_words, AlignmentSettings
import editdistance

settings = AlignmentSettings()
# Return the edit distance between the original and correction
settings.calc_distance = lambda original, correction: editdistance.distance(original, correction)
# Return an override of the distance and the error type; if error type is None the distance
# returned will be ignored
settings.detect_error = lambda original, correction: (1, "s:r:gc:art") if original == "de" and correction == "het" else (0, None)
# How many words could be split from one?
# e.g. das -> da(t) (i)s requires a lookahead of 2
# hoest -> hoe (i)s (he)t requires a lookahead of 3
settings.lookahead = 5

transcript = input("Transcript: ")
correction = input("Correction: ")
alignment = align_words(transcript, correction, settings)
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

### Run Tests

```bash
pip install pytest
pytest
```

### Upload to PyPi

```bash
pip install pip-tools
python setup.py sdist
twine upload dist/*
```

## Acknowledgments

The research for this software was made possible by the CLARIAH-PLUS project financed by NWO (Grant 184.034.023).
