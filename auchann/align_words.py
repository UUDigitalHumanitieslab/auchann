from typing import Iterable, List, Tuple
from enum import Enum, unique
from auchann.correct_parenthesize import correct_parenthesize, fillers, fragments
from auchann.replacement_errors import detect_error
from sastadev.deregularise import correctinflection
import editdistance


@unique
class TokenOperation(Enum):
    INSERT = 1
    REPLACE = 2
    REMOVE = 3
    COPY = 4


class TokenCorrection:
    insert: List[str]
    remove: List[str]
    operation: TokenOperation
    is_filler: bool
    is_fragment: bool
    previous = None
    next = None
    errors = None

    def __init__(self,
                 operation: TokenOperation,
                 insert: List[str] = None,
                 remove: List[str] = None,
                 errors: List[str] = None):
        self.operation = operation
        self.insert = insert or [None]
        self.remove = remove or [None]
        self.errors = errors or [None]

        self.is_filler = operation == TokenOperation.REMOVE and len(
            remove) == 1 and remove[0] in fillers

        self.is_fragment = operation == TokenOperation.REMOVE and len(
            remove) == 1 and remove[0] in fragments

    def copy(self):
        return TokenCorrection(self.operation, self.insert.copy(), self.remove.copy(), self.errors.copy())

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
            return f'<{remove}> [//]'  # changed to <> [//] because of chamd test
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


distance_hash = {}


def calc_distance(original: str, correction: str) -> Tuple[int, str]:
    try:
        return distance_hash[original][correction]
    except KeyError:
        pass

    error = detect_error(original, correction)
    if error is None:
        for candidate, candidate_error in correctinflection(original):
            if candidate == correction:
                error = candidate_error
                break

    if error is None:
        distance = editdistance.distance(original, correction)
    else:
        distance = 1

    # don't allow too strong of an edit distance (prevent gibberish replacement)
    wordlen = max(len(original), len(correction))
    if distance > 0.5 * wordlen:
        distance = wordlen

    if original not in distance_hash:
        distance_hash[original] = {}
    if correction not in distance_hash:
        distance_hash[correction] = {}

    distance_hash[original][correction] = distance, error
    if error is None and original not in distance_hash[correction]:
        distance_hash[correction][original] = distance, None

    return distance, error


def align_words(transcript: str, correction: str) -> TokenAlignments:
    transcript_tokens = transcript.split()
    correction_tokens = correction.split()
    session = AlignmentSession(transcript_tokens, correction_tokens)
    alignments = session.align_tokens()
    for alignment in alignments:
        alignment.group()

    # pick the alignment with the minimum number of corrections
    alignments.sort(key=lambda alignment: len(alignment.corrections))

    return alignments[0]


def prepend_correction(correction: TokenCorrection,
                       distance: int,
                       alignments: Iterable[TokenAlignments]) -> Iterable[TokenAlignments]:
    for alignment in alignments:
        yield TokenAlignments([correction] + alignment.corrections, distance + alignment.distance)


class AlignmentSession:
    def __init__(self, transcript_tokens: List[str], correction_tokens: List[str]):
        self.transcript_tokens = transcript_tokens
        self.correction_tokens = correction_tokens
        self.hash = {}

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
                            TokenOperation.INSERT, self.correction_tokens[correction_offset:])],
                        len(''.join(self.correction_tokens[correction_offset:])))]
        elif correction_offset >= len(self.correction_tokens):
            return [TokenAlignments(
                [TokenCorrection(TokenOperation.REMOVE, None,
                                 self.transcript_tokens[transcript_offset:])],
                len(''.join(self.transcript_tokens[transcript_offset:])))]

        # FIND THE MINIMAL DISTANCE
        alignments = self.align_replace(transcript_offset, correction_offset) + \
            self.align_insert(transcript_offset, correction_offset) + \
            self.align_remove(transcript_offset, correction_offset)

        alignments.sort(key=lambda alignment: alignment.distance)

        min_distance = alignments[0].distance
        for alignment in list(alignments):
            if alignment.distance > min_distance:
                alignments.remove(alignment)

        return alignments

    def align_replace(self, transcript_offset: int, correction_offset: int) -> List[TokenAlignments]:
        # OPTION 1: replacement/copy operation
        distance, error = calc_distance(
            self.transcript_tokens[transcript_offset], self.correction_tokens[correction_offset])

        correction = TokenCorrection(
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
            TokenOperation.INSERT, [self.correction_tokens[correction_offset]])

        return list(prepend_correction(correction, distance, alignment))

    def align_remove(self, transcript_offset: int, correction_offset: int) -> List[TokenAlignments]:
        # OPTION 3: remove transcript token
        alignment = self.align_tokens(transcript_offset+1, correction_offset)
        distance = len(self.transcript_tokens[transcript_offset])

        correction = TokenCorrection(
            TokenOperation.REMOVE, None, [self.transcript_tokens[transcript_offset]])

        return list(prepend_correction(correction, distance, alignment))
