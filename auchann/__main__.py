"""""
Created on 12-Jan-2022, 13:30
By Mees van Stiphout
"""""

from multiprocessing.sharedctypes import Value
import sys
import os
from typing import List
from chamd import ChatReader
import re


def remove_line_annotations(line: List[str]):
    """
    Removes all CHAT annotations/additions
    """
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
                item = item.replace(bb.group(), "")  # remove everything between brackets within an item
            if len(item) > 0:
                replacement_line.append(item)  # add item w/o supplements to repl_line if there is any left
            else:
                pass
        elif item[0] == '[':  # leave out corrections, guesses, and extra information, which can be spread over several items, hence the correction_status
            correction_status = True
        elif correction_status == True:  # if item is part of a correction, leave it out
            if item[-1] in ["]"]:  # look for end of correction
                correction_status = False
        elif "@" in item:  # if special form marker, only keep item in front of it
            item = item.split("@")[0]
            replacement_line.append(item)

        else:
            replacement_line.append(item.strip("<>"))  # strip item of '<' and '>', used to mark range of paralinguistic event
    return(replacement_line)

def chat_lines(file):
    for line in file:
        if not line[0] in ['@', '%']:
            og_line = remove_line_annotations(line.split())
            yield " ".join(og_line)

#Read CHA file and recreate the original transcription by replacing the CHAT annotations with the original utterances
def remove_file_annotations(filepath, filedestinationpath):
    with open(filepath) as file:
        transcript_name = os.path.splitext(filepath)[0].split('/')[-1]
        if not os.path.exists(filedestinationpath):
            os.makedirs(filedestinationpath)
        with open((filedestinationpath + '/' + transcript_name + '_de-annotated.txt'), 'w') as newfile:
            for line in chat_lines(file):
                newfile.write(line)
                newfile.write("\n")



def main(args=None):
    export_path = ""
    path_to_cha_files = ""
    # arguments are stored in an array called args
    if args is None:
        args = sys.argv[1:]
        try:
            path_to_cha_files = args[0]
            if len(args) == 1:
                export_path = os.getcwd()
            if len(args) == 2:
                export_path = args[1]
        except ValueError:
            print("Provide between 1 and 2 arguments, as follows: python auchann <path_to_cha_file(s)> <export_path (optional)>")
    

    # path_to_cha_files = "chafiles/laura02.cha"
    # export_path = "chafiles/og_files/laura02test.txt"
    """
    Users need to specify a path to a folder with cha files or a cha file, and optionally a path for the exported file to be stored
    Default export path is current directory (os.getcwd())
    """
    if os.path.splitext(path_to_cha_files)[1] == ".cha":  # if it is a single chat file
        remove_file_annotations(path_to_cha_files, export_path)
        print("De-annotation Succesful! Converted .cha file to de-annotated text at {}.".format(export_path))

    else:
        conversion_counter = 0
        for filename in os.listdir(path_to_cha_files):
            if os.path.splitext(filename)[-1] == ".cha":  
                remove_file_annotations((path_to_cha_files + '/' + filename), export_path)
                conversion_counter += 1
        print("De-annotation Succesful! Converted {} .cha files to de-annotated text at {}.".format(conversion_counter, export_path))
        
                
            



if __name__ == "__main__":
    main()
