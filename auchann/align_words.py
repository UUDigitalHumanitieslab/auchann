from typing import Iterable, List
from enum import Enum, unique
from correct_parenthesize import correct_parenthesize, fillers
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

    def __init__(self, operation: TokenOperation, insert: List[str] = None, remove: List[str] = None):
        self.operation = operation
        self.insert = insert or [None]
        self.remove = remove or [None]

        self.is_filler = operation == TokenOperation.REMOVE and len(
            remove) == 1 and remove[0] in fillers

        self.is_fragment = operation == TokenOperation.REMOVE and len(
            remove[0]) == 1

    def copy(self):
        return TokenCorrection(self.operation, self.insert.copy(), self.remove.copy())

    def __str__(self):
        if self.operation == TokenOperation.COPY:
            return ' '.join(self.insert)
        elif self.operation == TokenOperation.INSERT:
            return ' '.join(f'0{insert}' for insert in self.insert)
        elif self.operation == TokenOperation.REMOVE:
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
        elif self.operation == TokenOperation.REPLACE:
            return ' '.join(correct_parenthesize(original, correction)
                            for (original, correction) in zip(self.remove, self.insert))
        else:
            return f'UNKNOWN OPERATION {self.operation}'


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


def calc_distance(a: str, b: str):
    try:
        return distance_hash[a][b]
    except KeyError:
        pass

    distance = editdistance.distance(a, b)

    # don't allow too strong of an edit distance (prevent gibberish replacement)
    wordlen = max(len(a), len(b))
    if distance > 0.5 * wordlen:
        distance = wordlen

    if a not in distance_hash:
        distance_hash[a] = {}
    if b not in distance_hash:
        distance_hash[b] = {}

    distance_hash[a][b] = distance
    distance_hash[b][a] = distance

    return distance


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


def prepend_correction(correction: TokenCorrection, distance: int, alignments: Iterable[TokenAlignments]) -> Iterable[TokenAlignments]:
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
                return [TokenAlignments([TokenCorrection(TokenOperation.INSERT, self.correction_tokens[correction_offset:])], len(''.join(self.correction_tokens[correction_offset:])))]
        elif correction_offset >= len(self.correction_tokens):
            return [TokenAlignments([TokenCorrection(TokenOperation.REMOVE, None, self.transcript_tokens[transcript_offset:])], len(''.join(self.transcript_tokens[transcript_offset:])))]

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
        distance = calc_distance(
            self.transcript_tokens[transcript_offset], self.correction_tokens[correction_offset])

        correction = TokenCorrection(
            TokenOperation.COPY if distance == 0 else TokenOperation.REPLACE,
            [self.correction_tokens[correction_offset]],
            [self.transcript_tokens[transcript_offset]])

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
