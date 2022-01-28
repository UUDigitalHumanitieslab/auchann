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


def remove_line_annotations(line: str()):
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
                item = item.replace(bb.group(), "")  # remove everything between brackets within an item
            if len(item) > 0:
                replacement_line.append(item)  # add item w/o supplements to repl_line if there is any left
            else:
                pass
        elif item in ['[.]', '[?]', '[*]','[*s]','[*m]','[*gram]', '[<]', '[>]', '[!]', '[!!]', '[+bch]', '[/]', '[//]', '[///]']:  # all single-item markers between brackets
            pass
        elif item[0:2] in ['[:', '[=', '[#', '[%', '[+', '[-']:  # leave out corrections, guesses, and extra information, which can be spread over several items, hence the correction_status
            correction_status = True
        elif correction_status == True:  # if item is part of a correction, leave it out
            if item[-1] in ["]"]:  # look for end of correction
                correction_status = False
        elif "@" in item:  # if special form marker, only keep item in front of it
            item = item.split("@")[0]
            replacement_line.append(item)

        else:
            replacement_line.append(item.strip("<>&+-"))  # strip item of '<' and '>', used to mark range of paralinguistic event
    return(" ".join(replacement_line))


def correct_line(line: str()):
    """
    Removes all CHAT annotations/additions and returns a corrected string
    """
    line = line.split()


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


def chat_lines(file):
    """
    Runs through lines in a chat file, filtering out extralinguistic details
    """
    for line in file:
        if not line[0] in ['@', '%']:
            transcript_line = remove_line_annotations(line)
            correction_line = correct_line(line)
            yield transcript_line, correction_line

#Read CHA file and recreate the original transcription by replacing the CHAT annotations with the original utterances
def remove_file_annotations(filepath, filedestinationpath):
    ### Make a .txt,/.cha input file route
    with open(filepath) as file:
        transcript_name = os.path.splitext(filepath)[0].split('/')[-1]
        if not os.path.exists(filedestinationpath):
            os.makedirs(filedestinationpath)

        with open((filedestinationpath + '/' + transcript_name + '.txt'), 'w') as newfile:
            for line in chat_lines(file):
                newfile.write(line[0])
                newfile.write("\n")


class spokenline:
    """
    A class that contains the three versions of the transcript, i.e. the original, the correction, and the CHAT-annotated version, as well as some metadata, i.e. speaker, linenr, and corpus
    Contains a single line/utterance which can be converted to a dictionary to add to a yaml file
    """
    def __init__(self, line, speaker, corpus, chat, correction, transcript):
        self.line = line
        self.speaker = speaker
        self.corpus = corpus
        self.chat = chat
        self.correction = correction
        self.transcript = transcript
    
    def chat_to_transcript(self):
        self.transcript = remove_line_annotations(self.chat)

    def chat_to_correction(self):
        self.correction = cleanCHILDESMD.cleantext(self.chat, False)  # use chamd to clean string to correction, False is to remove repititions, set to True if you want to keep repititions

    def transcript_and_correction_to_chat(self):
        ##placeholder
        pass

    def convert_to_dictionary(self):
        yaml_dict = {
            'meta':{
                'line': self.line,
                'speaker': self.speaker,
                'corpus': self.corpus
            }, 
            'content':{
                'CHAT': self.chat,
                'correction': self.correction,
                'transcript': self.transcript
            }}
        return yaml_dict



def main(args=None):
    yamlfile = ""
    ##read the yaml and match transcript to correction
    if args is None:  # everything after 'auchann' is taken as an argument
        args = sys.argv[1:]
        try:
            yamlfile = args[0]
        except ValueError:
            print("Provide a .yaml file as your first argument following the correct format")

    with open(yamlfile, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)  # loads a yaml file that contains a list of dictionaries, one for every line
        lines = data["lines"]

        
    
        

            



if __name__ == "__main__":
    main()
