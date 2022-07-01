# AuChAnn

[![Actions Status](https://github.com/UUDigitalHumanitieslab/auchann/workflows/Unit%20tests/badge.svg)](https://github.com/UUDigitalHumanitieslab/auchann/actions)

[pypi auchann](https://pypi.org/project/auchann)

AuChAnn is a python package that provides Automatic CHAT Annotation based on a transcript string and an interpretation (or 'corrected') string. For example, when given:
Transcript:      'Ik wilt nu eh na huis'
Correction:      'Ik wil nu naar huis'

AuChAnn produces:
CHAT-Annotation: 'ik wilt [: wil] nu &-eh na(ar) [* s:r:prep] huis'

CHAT is an annotation convention that was developed for the CHILDES corpus (MacWinney, 2000) and is used by many linguists to annotate speech. For more information on CHAT,  you can read their manual: https://talkbank.org/manuals/CHAT.html.

AuChAnn was specifically developed to enhance linguistic data in the form of a transcript and interpretation by a linguist for use with SASTA (https://github.com/UUDigitalHumanitieslab/sasta)

## Getting Started

You can install AuChAnn using pip:
```bash
pip install auchann
```

When installed, the program can be run interactively from the console using the command `auchann` .

## Import as Library

To use AuChAnn in your own python applications, you can import the align_words function from align_words, see below. This is the main functionality of the package.

```python
from auchann.align_words import align_words

transcript = input("Transcript: ")
correction = input("Correction: ")
alignment = align_words(transcript, correction)
print(alignment)
```

### Settings

Various settings can be adjusted. Default values are used for every unchanged property.

```python
from auchann.align_words import align_words, AlignmentSettings
import editdistance

settings = AlignmentSettings()

# Return the edit distance between the original and correction
settings.calc_distance = lambda original, correction: editdistance.distance(original, correction)

# Return an override of the distance and the error type;
# if error type is None the distance returned will be ignored
# Default method detects inflection errors
settings.detect_error = lambda original, correction: (1, "m") if original == "geloopt" and correction == "liep" else (0, None)

# How many words could be split from one?
# e.g. das -> da(t) (i)s requires a lookahead of 2
# hoest -> hoe (i)s (he)t requires a lookahead of 3
settings.lookahead = 5

# Allow detection of replacements within a group
# e.g. swapping articles this will then be marked with
# the specified key

# EXAMPLE:
# Transcript: de huis
# Correction: het huis
# de [: het] [* s:r:gc:art] huis
settings.replacements = {
    's:r:gc:art': ['de', 'het', 'een'],
    's:r:gc:pro': ['dit', 'dat', 'deze'],
    's:r:prep': ['aan', 'uit']
}

# Other lists to adjust
settings.fillers = ['eh', 'hm', 'uh']
settings.fragments = ['ba', 'to', 'mu']

### Example usage
transcript = input("Transcript: ")
correction = input("Correction: ")
alignment = align_words(transcript, correction, settings)
print(alignment)
```

## How it Works

The `align_words` function scans the transcript and correction and determines for each token whether a correction token is copied exactly from the transcript, replaces a token from the transcript, is inserted, or whether a transcript token has been omitted. Based on which of these operations has occurred, the function adds the appropriate CHAT annotation to the output string.

The algorithm uses edit distance to establish which words are replacements of each other, i.e. it links a transcript token to a correction token. Words with the lowest available edit distance are matched together, and based on this match the operations COPY and REPLACE are determined. If two candidates have the same edit distance to a token, word position is used to determine the match. The operations REMOVE and INSERT are established if no suitable match can be found for a transcript and correction token respectively.

In addition to establishing these four operations, the function detects several other properties of the transcript and correction which can be expressed in CHAT. For example, it determines whether a word is a filler or fragment, whether a conjugation error has occurred, or if a pronoun, preposition, or article has been used incorrectly.

## Development

To install the requirements:

```bash
pip install -r requirements.txt
```

To run the AuChAnn command-line function from the console:

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

## References

MacWhinney, B. (2000).  The CHILDES Project: Tools for Analyzing Talk. 3rd Edition.  Mahwah, NJ: Lawrence Erlbaum Associates
