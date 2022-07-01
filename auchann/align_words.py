from typing import cast, Callable, Dict, Iterable, List, Optional, Tuple, Union
from enum import Enum, unique
from auchann.correct_parenthesize import correct_parenthesize
import auchann.data as data
from sastadev.deregularise import correctinflection
import editdistance

chat_errors = {
    'Overgeneralisation': 'm',
    'Lacking ge prefix': 'm',
    'Prefix ge without onset': 'm',
    'Wrong Overgeneralisation': 'm',
    'Wrong -en suffix': 'm'
}


def map_error(error_type: str) -> str:
    try:
        return chat_errors[error_type]
    except KeyError:
        return error_type


@unique
class TokenOperation(Enum):
    INSERT = 1
    REPLACE = 2
    REMOVE = 3
    COPY = 4


class TokenCorrection:
    insert: List[Optional[str]]
    remove: List[Optional[str]]
    operation: TokenOperation
    is_filler: bool
    is_fragment: bool
    previous = None
    next = None
    errors = None

    def __init__(self,
                 settings: 'AlignmentSettings',
                 operation: TokenOperation,
                 insert: Union[None, List[str], List[Optional[str]]] = None,
                 remove: Union[None, List[str], List[Optional[str]]] = None,
                 errors: Union[None, List[str], List[Optional[str]]] = None):
        self.settings = settings
        self.operation = operation
        self.insert = cast(List[Optional[str]],
                           insert or ([None] * len(remove or [])))
        self.remove = cast(List[Optional[str]],
                           remove or ([None] * len(self.insert)))
        self.errors = cast(List[Optional[str]],
                           errors or ([None] * len(self.insert)))

        assert len(self.insert) == len(self.remove)
        assert len(self.remove) == len(self.errors)

        self.is_filler = operation == TokenOperation.REMOVE and len(
            self.remove) == 1 and self.remove[0] in settings.fillers

        self.is_fragment = operation == TokenOperation.REMOVE and len(
            self.remove) == 1 and self.remove[0] in settings.fragments

    def copy(self):
        return TokenCorrection(self.settings, self.operation, self.insert.copy(), self.remove.copy(), self.errors.copy())

    def __str__(self):
        if self.operation == TokenOperation.COPY:
            return ' '.join(self.insert)
        elif self.operation == TokenOperation.INSERT:
            return ' '.join(f'0{insert}' for insert in self.insert)
        elif self.operation == TokenOperation.REMOVE:
            return self.__str__remove()
        elif self.operation == TokenOperation.REPLACE:
            return ' '.join(correct_parenthesize(original, correction, error)
                            for (original, correction, error) in zip(self.remove, self.insert, self.errors))
        else:
            return f'UNKNOWN OPERATION {self.operation}'

    def __str__remove(self):
        remove = ' '.join(self.remove)
        if self.is_filler:
            return f'&-{remove}'
        if self.is_fragment:
            return f'&+{remove}'
        if self.previous is None:
            # changed to <> [//] because of chamd test
            return f'<{remove}> [//]'
        else:
            # repetition e.g. "bah [x 3]"
            repeat = 1
            for token in self.remove:
                if self.previous.operation == TokenOperation.COPY and \
                        self.previous.insert[-1] == token:
                    repeat += 1
                else:
                    repeat = -1
                    break
            if repeat == 2:
                return f'[/] {remove}'
            elif repeat > 2:
                return f'[x {repeat}]'

        # retracing e.g. "gi [//] gingen"
        if self.next is not None and \
                self.next.insert and \
                self.next.insert[0] is not None and \
                self.next.insert[0].startswith(remove):
            return f'{remove} [//]'
        return f'<{remove}> [//]'


class TokenAlignments:
    def __init__(self, corrections: List[TokenCorrection], distance: int):
        self.corrections = corrections
        self.distance = distance

    def group(self):
        """
        Group corrections spanning multiple tokens
        """
        grouped: List[TokenCorrection] = []
        previous = None
        for item in (item.copy() for item in self.corrections):
            # the same correction could be in different alignments
            # modifying it, would also modify those alignments
            if previous is not None:
                if previous.operation == item.operation and  \
                        not previous.is_filler and \
                        not item.is_filler:
                    previous.insert += item.insert
                    previous.remove += item.remove
                    previous.errors += item.errors
                    continue
                else:
                    previous.next = item

            grouped.append(item)
            item.previous = previous
            previous = item
        self.corrections = grouped

    def __str__(self):
        return ' '.join(str(correction) for correction in self.corrections)


class AlignmentSettings:
    distance_hash: Dict[str, Dict[str, Tuple[int, Optional[str]]]] = {}

    def __init__(self):
        self.lookahead = 2
        self.replacements = data.replacements
        self.fillers = data.fillers
        self.fragments = data.fragments

        def __calc_distance(original: str, correction: str) -> int:
            distance = editdistance.distance(original, correction)

            # don't allow too strong of an edit distance (prevent gibberish replacement)
            wordlen = max(len(original), len(correction))
            if distance > 0.5 * wordlen:
                distance = wordlen

            return distance

        def __detect_error(original: str, correction: str) -> Tuple[int, Optional[str]]:
            error = None
            for candidate, candidate_error in correctinflection(original):
                if candidate == correction:
                    error = map_error(candidate_error)
            if error is not None:
                return 1, cast(str, error)
            else:
                return 0, None

        self.__calc_distance = __calc_distance
        self.__detect_error = __detect_error

    @property
    def calc_distance(self):
        def method(original: str, correction: str) -> Tuple[int, Optional[str]]:
            try:
                return self.distance_hash[original][correction]
            except KeyError:
                pass

            distance, error = self.replacement_error(original, correction)
            if error is None:
                distance, error = self.detect_error(original, correction)
            if error is None:
                distance = self.__calc_distance(original, correction)

            if original not in self.distance_hash:
                self.distance_hash[original] = {}
            if correction not in self.distance_hash:
                self.distance_hash[correction] = {}

            self.distance_hash[original][correction] = distance, error
            if error is None and original not in self.distance_hash[correction]:
                self.distance_hash[correction][original] = distance, None

            return distance, error
        return method

    @calc_distance.setter
    def calc_distance(self, method: Callable[[str, str], int]):
        self.__calc_distance = method
        self.distance_hash = {}

    @property
    def lookahead(self):
        return self._lookahead

    @lookahead.setter
    def lookahead(self, value: int):
        self._lookahead = value
        self.split_lookaheads = list(i + 2 for i in range(value))
        self.distance_hash = {}

    @property
    def detect_error(self):
        return self.__detect_error

    @detect_error.setter
    def detect_error(self, method: Callable[[str, str], Tuple[int, Optional[str]]]):
        self.__detect_error = method
        self.distance_hash = {}

    def replacement_error(self, original: str, correction: str) -> Tuple[int, Optional[str]]:
        if original == correction:
            return 0, None

        for error, items in self.replacements.items():
            if original in items and correction in items:
                return 1, error

        return 0, None


def align_words(transcript: str, correction: str, settings: AlignmentSettings = None) -> TokenAlignments:
    transcript_tokens = transcript.split()
    correction_tokens = correction.split()
    session = AlignmentSession(
        transcript_tokens, correction_tokens, settings or AlignmentSettings())
    alignments = session.align_tokens()
    for alignment in alignments:
        alignment.group()

    # pick the alignment with the minimum number of corrections
    alignments.sort(key=lambda alignment: len(alignment.corrections))

    return alignments[0]


def align_split(transcript: str, corrections: List[str]) -> List[str]:
    """"
    Attempts to split a transcript into parts aligned with the corrections.
    e.g.
        was -> wat is -> ['wa', 's'] <wa(t) (i)s>
        hoest -> hoe is het -> ['hoe', 's', 't'] <hoe (i)s (he)t>
    """

    transcript_i = 0
    split: List[str] = []

    for i in range(0, len(corrections)):
        correction_i = 0
        match_start = -1
        while transcript_i < len(transcript) and correction_i < len(corrections[i]):
            t = transcript[transcript_i]
            c = corrections[i][correction_i]
            if t == c:
                if match_start == -1:
                    # match starts here e.g. was -> ... (i)s
                    match_start = transcript_i
                correction_i += 1
                transcript_i += 1
            elif match_start >= 0:
                # it stops here e.g. was -> wa(s) ...
                break
            else:
                # skipped character at the start
                correction_i += 1

        if match_start == -1:
            # no match found, abort
            return []

        split.append(transcript[match_start:transcript_i])

    # failed at the end
    return split if transcript_i == len(transcript) else []


def prepend_correction(correction: TokenCorrection,
                       distance: int,
                       alignments: Iterable[TokenAlignments]) -> Iterable[TokenAlignments]:
    for alignment in alignments:
        yield TokenAlignments([correction] + alignment.corrections, distance + alignment.distance)


class AlignmentSession:
    def __init__(self, transcript_tokens: List[str], correction_tokens: List[str], settings: AlignmentSettings):
        self.transcript_tokens = transcript_tokens
        self.correction_tokens = correction_tokens
        self.settings = settings
        self.hash: Dict[int, Dict[int, List[TokenAlignments]]] = {}

    def align_tokens(self, transcript_offset: int = 0, correction_offset: int = 0) -> List[TokenAlignments]:
        try:
            transcript_hash = self.hash[transcript_offset]
        except KeyError:
            transcript_hash = {}
            self.hash[transcript_offset] = transcript_hash

        try:
            return transcript_hash[correction_offset]
        except KeyError:
            pass

        alignment = self.__calc_align_tokens(
            transcript_offset, correction_offset)
        self.hash[transcript_offset][correction_offset] = alignment
        return alignment

    def __calc_align_tokens(self, transcript_offset: int, correction_offset: int) -> List[TokenAlignments]:
        # don't count spaces for the length
        # otherwise these are penalized (compared with option 1 and 2)
        if transcript_offset >= len(self.transcript_tokens):
            if correction_offset >= len(self.correction_tokens):
                return [TokenAlignments([], 0)]
            else:
                return [
                    TokenAlignments(
                        [TokenCorrection(
                            self.settings,
                            TokenOperation.INSERT,
                            self.correction_tokens[correction_offset:])],
                        len(''.join(self.correction_tokens[correction_offset:])))]
        elif correction_offset >= len(self.correction_tokens):
            return [TokenAlignments(
                [TokenCorrection(
                    self.settings,
                    TokenOperation.REMOVE,
                    None,
                    self.transcript_tokens[transcript_offset:])],
                len(''.join(self.transcript_tokens[transcript_offset:])))]

        # FIND THE MINIMAL DISTANCE
        # align replace multiple
        alignments = self.align_replace(transcript_offset, correction_offset) + \
            self.align_insert(transcript_offset, correction_offset) + \
            self.align_remove(transcript_offset, correction_offset) + \
            self.align_split(transcript_offset, correction_offset,
                             self.settings.split_lookaheads)

        alignments.sort(key=lambda alignment: alignment.distance)

        min_distance = alignments[0].distance
        for alignment in list(alignments):
            if alignment.distance > min_distance:
                alignments.remove(alignment)

        return alignments

    def align_replace(self, transcript_offset: int, correction_offset: int) -> List[TokenAlignments]:
        # OPTION 1: replacement/copy operation
        distance, error = self.settings.calc_distance(
            self.transcript_tokens[transcript_offset], self.correction_tokens[correction_offset])

        correction = TokenCorrection(
            self.settings,
            TokenOperation.COPY if distance == 0 else TokenOperation.REPLACE,
            [self.correction_tokens[correction_offset]],
            [self.transcript_tokens[transcript_offset]],
            [error])

        alignments = self.align_tokens(
            transcript_offset+1, correction_offset+1)

        return list(prepend_correction(correction, distance, alignments))

    def align_insert(self, transcript_offset: int, correction_offset: int) -> List[TokenAlignments]:
        # OPTION 2: insert correction token
        alignment = self.align_tokens(transcript_offset, correction_offset+1)
        distance = len(self.correction_tokens[correction_offset])

        correction = TokenCorrection(
            self.settings,
            TokenOperation.INSERT,
            [self.correction_tokens[correction_offset]])

        return list(prepend_correction(correction, distance, alignment))

    def align_remove(self, transcript_offset: int, correction_offset: int) -> List[TokenAlignments]:
        # OPTION 3: remove transcript token
        alignment = self.align_tokens(transcript_offset+1, correction_offset)
        distance = len(self.transcript_tokens[transcript_offset])

        correction = TokenCorrection(
            self.settings,
            TokenOperation.REMOVE,
            None,
            [self.transcript_tokens[transcript_offset]])

        return list(prepend_correction(correction, distance, alignment))

    def align_split(self,
                    transcript_offset: int,
                    correction_offset: int,
                    split_lookaheads: List[int]) -> List[TokenAlignments]:
        # OPTION 4: detect split of one word into two words e.g. was -> wat is
        corrections: List[TokenAlignments] = []
        for lookahead in split_lookaheads:
            if correction_offset + lookahead > len(self.correction_tokens):
                break

            transcript_token = self.transcript_tokens[transcript_offset]
            correction_tokens = self.correction_tokens[correction_offset:correction_offset+lookahead]
            split = align_split(
                transcript_token,
                correction_tokens)

            if split:
                correction = TokenCorrection(
                    self.settings,
                    TokenOperation.REPLACE,
                    correction_tokens,
                    split)

                alignment = self.align_tokens(
                    transcript_offset+1, correction_offset+lookahead)
                distance = sum(len(token)
                               for token in correction_tokens) - len(transcript_token)

                corrections += prepend_correction(
                    correction,
                    distance,
                    alignment)

        return corrections
