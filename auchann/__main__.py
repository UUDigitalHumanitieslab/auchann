"""""
Created on 12-Jan-2022, 13:30
By Mees van Stiphout
"""""

import sys
from chamd import ChatReader
import re


#reader = ChatReader()
# chat = reader.read_file('example.cha') # or read_string

# for item in chat.metadata:
#     print(item)
# for line in chat.lines:
#     for item in line.metadata:
#         print(item)
#     print(line.text)



# read CHA file and convert to transcript
# with open("chafiles/laura01.cha") as file:
# reader = ChatReader()
# chat = reader.read_file("chafiles/laura01.cha")

#for line in chat.lines:
    # for item in line.metadata:
    #     print(item)
    # print(line.text)


# function to remove all CHAT annotations/additions
def remove_line_annotations(line=list()):
    replacement_line = [line[0]]
    correction_status = False  # initialize correction status
    for item in line[1:]: 
        if item[0] == "0":  # leave out word insertions starting with '0'
            pass
        elif re.search(r"\(.*?\)", item):  # leave out supplements to words in brackets
            between_brackets = re.finditer(r"\(.*?\)", item)
            for bb in between_brackets:
                item = item.replace(bb.group(), "")  # remove everything between brackets within an item
            if len(item) > 0:
                replacement_line.append(item)  # add item w/o supplements to repl_line if there is any left
            else:
                pass
        elif item[0] == '[':  # leave out corrections, guesses, and extra information, which can be spread over several items, hence the correction_status
            correction_status = True
            pass
        elif correction_status == True:  # if item is part of a correction, leave it out
            if item[-1] in ["]"]:  # look for end of correction
                correction_status = False
            pass
        elif "@" in item:  # if special form marker, only keep item in front of it
            item = item.split("@")[0]
            replacement_line.append(item)

        else:
            replacement_line.append(item)
    return(replacement_line)


#Read CHA file and recreate the original transcription by replacing the CHAT annotations with the original utterances
def remove_file_annotations(filepath, filedestinationpath):
    with open(filepath) as file:
        replacement_file = []
        for line in file:
            if line[0] in ['@', '%']:
                replacement_file.append(line.split())
            else:
                og_line = remove_line_annotations(line.split())
                replacement_file.append(og_line)
        with open(filedestinationpath, 'w') as newfile:
            for line in replacement_file:
                newfile.write(" ".join(line))
                newfile.write("\n")



def main(args=None):
    # arguments are stored in an array called args
    if args is None:
        args = sys.argv[1:]

    path_to_cha_file = "chafiles/laura02.cha"
    path_to_new_file = "chafiles/og_files/laura02test.txt"
    remove_file_annotations(path_to_cha_file, path_to_new_file)


if __name__ == "__main__":
    main()
