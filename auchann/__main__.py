"""""
Created on 12-Jan-2022, 13:30
By Mees van Stiphout
"""""

from multiprocessing.sharedctypes import Value
import sys
import os
from typing import List
from chamd import ChatReader, cleanCHILDESMD
import re
import yaml
from auchann.remove_line_annotations import remove_line_annotations
from auchann.chat_annotate import chat_annotate


class Spokenline:
    """
    A class that contains the three versions of the transcript, i.e. the original, the correction, 
    and the CHAT-annotated version, as well as some metadata, i.e. speaker, linenr, and corpus.
    Contains a single line/utterance which can be converted to a dictionary to add to a yaml file.
    """

    def __init__(self, line, speaker, corpus, chat, correction, transcript):
        self.line = line
        self.speaker = speaker
        self.corpus = corpus
        self.chat = chat
        self.correction = correction
        self.transcript = transcript

    def chat_to_transcript(self):
        """
        Removes CHAT annotations from a line and returns a raw transcript line
        """
        self.transcript = remove_line_annotations(self.chat)

    def chat_to_correction(self):
        """
        Removes CHAT annotations from a line using chamd and returns a corrected transcript line
        """
        # use chamd to clean string to correction, False is to remove repititions, set to True if you want to keep repititions
        self.correction = cleanCHILDESMD.cleantext(self.chat, False)

    def transcript_and_correction_to_chat(self):
        """
        Adds CHAT annotation to the raw transcript based on the corrections, returns a CHAT-annotated line
        """
        self.CHAT = chat_annotate(self.transcript, self.correction)

    def convert_to_dictionary(self):
        """
        Coverts a line to a dictionary in the yaml format, returns that line as a dictionary that tains the raw transcript,
        correction, and CHAT-annotated line.
        """
        yaml_dict = {
            'meta': {
                'line': self.line,
                'speaker': self.speaker,
                'corpus': self.corpus
            },
            'content': {
                'CHAT': self.chat,
                'correction': self.correction,
                'transcript': self.transcript
            }}
        return yaml_dict


def main(args=None):
    yamlfile = ""
    # read the yaml and match transcript to correction
    if args is None:  # everything after 'auchann' is taken as an argument
        args = sys.argv[1:]
        try:
            yamlfile = args[0]
        except IndexError:
            print(
                "INDEX ERROR: Provide a .yaml filepath as your first argument following the correct format")
            exit()

    with open(yamlfile, 'r') as file:
        # loads a yaml file that contains a list of dictionaries, one for every line
        data = yaml.load(file, Loader=yaml.FullLoader)
        lines = data["lines"]


if __name__ == "__main__":
    main()
