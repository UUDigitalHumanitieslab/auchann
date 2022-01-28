from multiprocessing.sharedctypes import Value
import sys
import os
from typing import List
from chamd import ChatReader, cleanCHILDESMD
from auchann import __main__
import re
import yaml

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
        __main__.remove_file_annotations(path_to_cha_files, export_path)
        print("De-annotation Succesful! Converted .cha file to de-annotated text at {}.".format(export_path))

    else:
        conversion_counter = 0
        for filename in os.listdir(path_to_cha_files):
            if os.path.splitext(filename)[-1] == ".cha":  
                __main__.remove_file_annotations((path_to_cha_files + '/' + filename), export_path)
                conversion_counter += 1
        print("De-annotation Succesful! Converted {} .cha files to de-annotated text at {}.".format(conversion_counter, export_path))                
            
if __name__ == "__main__":
    main()