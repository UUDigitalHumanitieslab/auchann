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
    previous = None
    next = None

    def __init__(self, operation: TokenOperation, insert: List[str] = None, remove: List[str] = None):
        self.operation = operation
        self.insert = insert or [None]
        self.remove = remove or [None]

        self.is_filler = operation == TokenOperation.REMOVE and len(remove) == 1 and remove[0] in fillers

    def __str__(self):
        if self.operation == TokenOperation.COPY:
            return ' '.join(self.insert)
        elif self.operation == TokenOperation.INSERT:
            return ' '.join(f'0{insert}' for insert in self.insert)
        elif self.operation == TokenOperation.REMOVE:
            remove = ' '.join(self.remove)
            if self.is_filler:
                return f'&{remove}'
            if self.previous == None:
                return f'{remove} [///]'
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
            if self.next != None and \
                self.next.insert and \
                self.next.insert != None and \
                self.next.insert[0].startswith(remove):
                return f'{remove} [//]'
            return f'<{remove}> [//]'
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
            else:
                previous.next = item

        grouped.append(item)
        item.previous = previous
        previous = item
    return grouped


def align_tokens(transcript_tokens: List[str], correction_tokens: List[str]) -> Tuple[List[TokenCorrection], int]:
    # don't count spaces for the length
    # otherwise these are penalized (compared with option 1 and 2)
    if len(transcript_tokens) == 0:
        if len(correction_tokens) == 0:
            return [], 0
        else:
            return [TokenCorrection(TokenOperation.INSERT, correction_tokens)], len(''.join(correction_tokens))
    elif len(correction_tokens) == 0:
        return [TokenCorrection(TokenOperation.REMOVE, None, transcript_tokens)], len(''.join(transcript_tokens))

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
        [correction_tokens[0]],
        [transcript_tokens[0]])

    corrections, distance = align_tokens(
        transcript_tokens[1:], correction_tokens[1:])
    distance += first_distance

    # OPTION 2: insert correction token
    candidate_corrections, candidate_distance = align_tokens(
        transcript_tokens, correction_tokens[1:])
    candidate_distance += len(correction_tokens[0])

    if candidate_distance < distance:
        correction = TokenCorrection(
            TokenOperation.INSERT, [correction_tokens[0]])
        corrections = candidate_corrections
        distance = candidate_distance

    # OPTION 3: remove transcript token
    candidate_corrections, candidate_distance = align_tokens(
        transcript_tokens[1:], correction_tokens)
    candidate_distance += len(transcript_tokens[0])

    if candidate_distance < distance:
        correction = TokenCorrection(
            TokenOperation.REMOVE, None, [transcript_tokens[0]])
        corrections = candidate_corrections
        distance = candidate_distance

    return [correction] + corrections, distance
