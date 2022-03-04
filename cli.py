#!/usr/bin/env python3
from auchann.align_words import align_words

try:
    while True:
        transcript = input("Transcript: ")
        correction = input("Correction: ")
        alignment = align_words(transcript, correction)
        print(' '.join(str(correction) for correction in alignment.corrections))
except KeyboardInterrupt:
    pass
