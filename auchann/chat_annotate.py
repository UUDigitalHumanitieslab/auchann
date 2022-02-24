import re

fillers = [
    'eh',
    'ehm',
    'ah',
    'boe',
    'hm',
    'hmm',
    'uh',
    'uhm'
]


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
        i = 1

        for letter in original:
            pattern += (r'({})(.*)'.format(letter))
            replace_pattern += r'(\{})\{}'.format(i, i+1)
            i += 2

        pattern += r'(.*)'
        pattern = re.compile(pattern)

        # if the pattern is not in the correction,
        # a ()-notation is not possible
        # in this case, return [: ]-notation
        if not re.match(pattern, correction):
            return '{} [: {}]'.format(original, correction)

        # replace all diff with (diff)
        parenthesize = re.sub(pattern, replace_pattern, correction)

        # remove ()
        remove_empty = re.sub(r'\(\)', '', parenthesize)

        # split corrections with whitespace
        split_whitespace = re.sub(r'\((\S+)(\s+)(\S+)\)',
                                  r'(\1)\2(\3)', remove_empty)

        # if all else fails, just use the [: ] notation
        if not split_whitespace.replace('(', '').replace(')', '') == correction:
            return '{} [: {}]'.format(original, correction)

        return split_whitespace


def chat_annotate(transcript_dict, correction_dict):
    global fillers
    transcript_line = [key[0] for key in transcript_dict]
    correction_line = [key[0] for key in correction_dict]
    CHAT_line = []

    replacement_queue = []
    for key in transcript_dict:
        if transcript_dict[key] == False:
            if key[0] in fillers:
                CHAT_line.append(str('&' + key[0]))
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
        if correction_dict[key] == False:
            CHAT_line.insert(key[1], key[0])  # inserts word at corrected index

    return(' '.join(CHAT_line))
