import re
from typing import List

fillers = [
    'eh',
    'ehm',
    'ah',
    'boe',
    'hm',
    'hmm',
    'uh',
    'uhm',
    'ggg',
    'mmm',
    'ja',
    'nee'
]


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

    def step(self, offset: int, omitted: str, target: str):
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


def correct_parenthesize(original: str, correction: str) -> str:
    '''
    take a string and its corrected equivalent.
    calculate the differences between the two and parenthesizes these.
    differences with whitespace should be split.
    Taken from TrEd-bridge: https://github.com/UUDigitalHumanitieslab/TrEd-bridge/blob/fc56323cd8921724c23b33c63cfa7400e08d909f/functions.py#L200
    '''
    ws_pattern = re.compile(r'(\S+)\s+(\S+)')
    pattern = r'(.*)'
    replace_pattern = r''
    i = 1

    # if there is whitespace in the correction,
    # return [: ] form
    if re.search(r'\s+', correction):
        return '{} [: {}]'.format(original, correction)

    # segment repetition e.g. ga-ga-gaan
    segment_repetitions = original.split("-")[:-1]
    if segment_repetitions and \
        "-" not in correction and \
            all(correction.startswith(part) for part in segment_repetitions):
        reps = ('-'.join(segment_repetitions))
        return f'\u21AB{reps}\u21AB{correction}'

    # only edits at start or end
    if original in correction:
        pattern = r'(.*)({})(.*)'.format(original)
        replace_pattern = r'(\1)\2(\3)'

        parenthesize = re.sub(pattern, replace_pattern, correction)
        remove_empty = re.sub(r'\(\)', '', parenthesize)
        split_whitespace = re.sub(r'\((\S+)(\s+)(\S+)\)',
                                  r'(\1)\2(\3)', remove_empty)
        return split_whitespace

    else:
        pattern = r'(.*)'
        replace_pattern = r''
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

        # if the pattern is not in the correction,
        # a ()-notation is not possible
        # in this case, return [: ]-notation
        if not replacements:
            return '{} [: {}]'.format(original, correction)

        # minimize the number of segments and if multiple solutions exist
        # maximize for open segments i.e. ending with a vowel
        return str(sorted(
            replacements,
            key=lambda replacement: (replacement.omissions, -replacement.open_segments()))[0])


def chat_annotate(transcript_dict, correction_dict):
    global fillers
    transcript_line = [key[0] for key in transcript_dict]
    correction_line = [key[0] for key in correction_dict]
    CHAT_line = []

    replacement_queue = []
    for key in transcript_dict:
        if transcript_dict[key] is False:
            if key[0] in fillers:
                CHAT_line.append(str('&-' + key[0]))
            else:
                # TEMPORARY - need to find solution still
                CHAT_line.append(key[0])
        else:
            # if the edit distance is 0, simply append the word
            if transcript_dict[key][3] == 0:
                CHAT_line.append(key[0])
            else:
                correction = correct_parenthesize(
                    key[0], transcript_dict[key][1])
                CHAT_line.append(correction)

    for key in correction_dict:
        if correction_dict[key] is False:
            CHAT_line.insert(key[1], key[0])  # inserts word at corrected index

    return(' '.join(CHAT_line))
