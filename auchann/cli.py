#!/usr/bin/env python3

from auchann.align_words import align_words

try:
    while True:
        transcript = input("Transcript: ")
        correction = input("Correction: ")
        alignment = align_words(transcript, correction)
        print(alignment)
except KeyboardInterrupt:
    pass
