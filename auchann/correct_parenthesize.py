import re
from typing import List, Optional


class Segment:
    def __init__(self, text: str, is_omission: bool):
        self.text = text
        self.is_omission = is_omission

    def step(self, text: str, is_omission: bool):
        if self.is_omission == is_omission:
            return [Segment(self.text + text, is_omission)]
        else:
            return [self, Segment(text, is_omission)]


class Replacement:
    def __init__(self, target_position: int = 0, segments: List[Segment] = None, omissions: int = 0):
        self.__open_segments = None
        self.target_position = target_position
        self.segments = segments or []
        self.omissions = omissions

    def step(self, offset: int, omitted: str, target: Optional[str]):
        try:
            last_segment = self.segments[-1]
        except IndexError:
            last_segment = None

        new_segments = list(self.segments[:-1])
        omissions = self.omissions

        if omitted:
            if last_segment is None:
                last_segment = Segment(omitted, True)
                omissions += 1
            elif last_segment.is_omission:
                last_segment = Segment(last_segment.text + omitted, True)
            else:
                new_segments.append(last_segment)
                last_segment = Segment(omitted, True)
                omissions += 1

        if target is None:
            if last_segment:
                new_segments.append(last_segment)
        else:
            if last_segment is None:
                new_segments.append(Segment(target, False))
            else:
                for segment in last_segment.step(target, False):
                    new_segments.append(segment)

        return Replacement(
            self.target_position + offset + 1,
            new_segments,
            omissions)

    def open_segments(self):
        if self.__open_segments is None:
            count = 0
            for segment in self.segments:
                count += 1 if is_vowel(segment.text[-1]) else 0
            self.__open_segments = count
        return self.__open_segments

    def __str__(self):
        text = ""
        for segment in self.segments:
            if segment.is_omission:
                text += f"({segment.text})"
            else:
                text += segment.text
        return text


def is_vowel(char: str) -> bool:
    return char.lower() in ('a', 'e', 'u', 'i', 'o', 'y')


def correct_parenthesize(original: str, correction: str, error_type: str = None) -> str:
    """Takes a string and its corrected equivalent.
    Calculates the differences between the two and parenthesizes these.
    Differences with whitespace should be split.
    Based on TrEd-bridge:
    https://github.com/UUDigitalHumanitieslab/TrEd-bridge/blob/fc56323cd8921724c23b33c63cfa7400e08d909f/functions.py#L200

    Returns:
        str: CHAT notation for the correction
    """
    chat = whitespace_correction(original, correction) or \
        segment_repetition_correction(original, correction) or \
        parenthesize_correction(original, correction) or \
        fallback_correction(original, correction)

    return f'{chat} [* {error_type}]' if error_type else chat


def whitespace_correction(original: str, correction: str) -> Optional[str]:
    # if there is whitespace in the correction,
    # return [: ] form
    if re.search(r'\s+', correction):
        return fallback_correction(original, correction)

    return None


def segment_repetition_correction(original: str, correction: str) -> Optional[str]:
    # segment repetition e.g. ga-ga-gaan
    segment_repetitions = original.split("-")[:-1]
    if segment_repetitions and \
        "-" not in correction and \
            all(correction.startswith(part) for part in segment_repetitions):
        reps = ('-'.join(segment_repetitions))
        return f'\u21AB{reps}\u21AB{correction}'

    return None


def parenthesize_correction(original: str, correction: str) -> Optional[str]:
    replacements = [Replacement()]
    for letter in original:
        new_replacements = []
        for replacement in replacements:
            for offset, target in enumerate(correction[replacement.target_position:]):
                if target == letter:
                    omitted = correction[replacement.target_position:
                                         replacement.target_position+offset]

                    new_replacements.append(
                        replacement.step(offset, omitted, target))
        replacements = new_replacements

    for index, replacement in enumerate(replacements):
        leftover = correction[replacement.target_position:]
        if leftover:
            replacements[index] = replacement.step(0, leftover, None)

    # if the pattern is not in the correction,
    # a ()-notation is not possible
    if not replacements:
        return None

    # minimize the number of segments and if multiple solutions exist
    # maximize for open segments i.e. ending with a vowel
    return str(sorted(
        replacements,
        key=lambda replacement: (replacement.omissions, -replacement.open_segments()))[0])


def fallback_correction(original: str, correction: str) -> str:
    # [: ]-notation
    return '{} [: {}]'.format(original, correction)
