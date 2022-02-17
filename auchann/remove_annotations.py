from multiprocessing.sharedctypes import Value
import sys
import os
from typing import List
from chamd import ChatReader, cleanCHILDESMD
from auchann.remove_line_annotations import remove_line_annotations
from auchann import __main__

import re
import yaml


"""
This code is not currently used: method to convert .cha files to de-annotated .txt files.
"""


def chat_lines(file):
    """
    Runs through lines in a chat file, filtering out extralinguistic details
    """
    for line in file:
        if not line[0] in ['@', '%']:
            transcript_line = remove_line_annotations(
                line)
            correction_line = cleanCHILDESMD.cleantext(line, False)
            yield transcript_line, correction_line


def remove_file_annotations(filepath, filedestinationpath):
    # Make a .txt,/.cha input file route
    with open(filepath) as file:
        transcript_name = os.path.splitext(filepath)[0].split('/')[-1]
        if not os.path.exists(filedestinationpath):
            os.makedirs(filedestinationpath)

        with open((filedestinationpath + '/' + transcript_name + '.txt'), 'w') as newfile:
            for line in chat_lines(file):
                newfile.write(line[0])
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
    # export_path = "chafiles/og_files/"
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
                remove_file_annotations(
                    (path_to_cha_files + '/' + filename), export_path)
                conversion_counter += 1
        print("De-annotation Succesful! Converted {} .cha files to de-annotated text at {}.".format(
            conversion_counter, export_path))


if __name__ == "__main__":
    main()
