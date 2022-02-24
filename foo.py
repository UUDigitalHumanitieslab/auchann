#!/usr/bin/env python3

from auchann.align_words import align_words2

inputs = [
    ("dit is ee test", "dit is een test"),
    ("this is een test", "dit is een test"),
    ("dit is een test", "is een test"),
    ("dit uh is een test", "dit is een test"),
    ("dit is uh is is een test", "dit is een test"),
]

for transcript, correction in inputs:
    alignment = align_words2(transcript, correction)
    print(' '.join(str(correction) for correction in alignment))
