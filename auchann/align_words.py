from typing import List, Tuple
from enum import Enum, unique
from .chat_annotate import correct_parenthesize, fillers
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

    def __init__(self, operation: TokenOperation, insert: str = None, remove: str = None):
        self.operation = operation
        self.insert = [insert]
        self.remove = [remove]

        self.is_filler = operation == TokenOperation.REMOVE and remove in fillers

    def __str__(self):
        if self.operation == TokenOperation.COPY:
            return ' '.join(self.insert)
        elif self.operation == TokenOperation.INSERT:
            return ' '.join(f'0{insert}' for insert in self.insert)
        elif self.operation == TokenOperation.REMOVE:
            remove = ' '.join(self.remove)
            if self.is_filler:
                return f'&{remove}'
            return f'<{remove}> [///]'
        elif self.operation == TokenOperation.REPLACE:
            return ' '.join(correct_parenthesize(original, correction)
                for (original, correction) in zip(self.remove, self.insert))
        else:
            return f'UNKNOWN OPERATION {self.operation}'


def align_words(transcript: str, correction: str) -> List[TokenCorrection]:
    transcript_tokens = transcript.split()
    correction_tokens = correction.split()
    alignment, distance = align_tokens(transcript_tokens, correction_tokens)

    grouped: List[TokenCorrection] = []
    previous = None
    for item in alignment:
        if previous is not None:
            if previous.operation == item.operation and  \
                    not previous.is_filler and \
                    not item.is_filler:
                previous.insert += item.insert
                previous.remove += item.remove
                continue

        grouped.append(item)
        previous = item
    return grouped


def align_tokens(transcript_tokens: List[str], correction_tokens: List[str]) -> Tuple[List[TokenCorrection], int]:
    if len(transcript_tokens) == 0:
        if len(correction_tokens) == 0:
            return [], 0
        else:
            insert = ' '.join(correction_tokens)
            return [TokenCorrection(TokenOperation.INSERT, insert)], len(insert)
    elif len(correction_tokens) == 0:
        remove = ' '.join(transcript_tokens)
        return [TokenCorrection(TokenOperation.REMOVE, None, remove)], len(remove)

    # FIND THE MINIMAL DISTANCE
    # OPTION 1: replacement/copy operation
    first_distance = editdistance.distance(
        transcript_tokens[0], correction_tokens[0])

    # don't allow too strong of an edit distance (prevent gibberish replacement)
    wordlen = max(len(transcript_tokens[0]), len(correction_tokens[0]))
    if first_distance > 0.5 * wordlen:
        first_distance = wordlen

    correction = TokenCorrection(
        TokenOperation.COPY if first_distance == 0 else TokenOperation.REPLACE,
        correction_tokens[0],
        transcript_tokens[0])

    corrections, distance = align_tokens(
        transcript_tokens[1:], correction_tokens[1:])
    distance += first_distance

    # OPTION 2: insert correction token
    candidate_corrections, candidate_distance = align_tokens(
        transcript_tokens, correction_tokens[1:])
    candidate_distance += len(correction_tokens[0])

    if candidate_distance < distance:
        correction = TokenCorrection(
            TokenOperation.INSERT, correction_tokens[0])
        corrections = candidate_corrections
        distance = candidate_distance

    # OPTION 3: remove transcript token
    candidate_corrections, candidate_distance = align_tokens(
        transcript_tokens[1:], correction_tokens)
    candidate_distance += len(transcript_tokens[0])

    if candidate_distance < distance:
        correction = TokenCorrection(
            TokenOperation.REMOVE, None, transcript_tokens[0])
        corrections = candidate_corrections
        distance = candidate_distance

    return [correction] + corrections, distance
