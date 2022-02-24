import re


def remove_line_annotations(line: str):
    """
    Removes all CHAT annotations/additions and returns the original transcript string
    """
    line = line.split()
    replacement_line = []
    correction_status = False  # initialize correction status
    for item in line:
        if item[0] == "0":  # leave out word insertions starting with '0'
            pass
        elif item[0:2] == "&=":  # leave out vocalization status
            pass
        elif re.search(r"\(.*?\)", item):  # leave out supplements to words in brackets
            between_brackets = re.finditer(r"\(.*?\)", item)
            for bb in between_brackets:
                # remove everything between brackets within an item
                item = item.replace(bb.group(), "")
            if len(item) > 0:
                # add item w/o supplements to repl_line if there is any left
                replacement_line.append(item)
            else:
                pass
        # all single-item markers between brackets
        elif item in ['[.]', '[?]', '[*]', '[*s]', '[*m]', '[*gram]', '[<]', '[>]', '[!]', '[!!]', '[+bch]', '[/]', '[//]', '[///]']:
            pass
        # leave out corrections, guesses, and extra information, which can be spread over several items, hence the correction_status
        elif item[0:2] in ['[:', '[=', '[#', '[%', '[+', '[-']:
            correction_status = True
        elif correction_status == True:  # if item is part of a correction, leave it out
            if item[-1] in ["]"]:  # look for end of correction
                correction_status = False
        elif "@" in item:  # if special form marker, only keep item in front of it
            item = item.split("@")[0]
            replacement_line.append(item)

        else:
            # strip item of '<' and '>', used to mark range of paralinguistic event
            replacement_line.append(item.strip("<>&+-"))
    return(" ".join(replacement_line))
