import yaml
import re
from chamd import ChatReader, cleanCHILDESMD

# Dictionairy of lines, containing dictionaries of meta and content per line, containing three entries per dictionairy
# So for each line, create a new dictionairy containing meta and content per line, which you can do in a class?

"""
How to process the .cha files from vKampen
"""
lines_dict = {'lines': []}

chat_path = 'chafiles/laura01.cha'
with open(chat_path, 'r') as chatfile:
    for i, line in enumerate(chatfile, start=1):
        if line[0] == '*':  # if the line is an utterance, process it
            linenr = i
            speaker = line.split()[0][1:]
            corpus = 'vKampen-Childes'
            chat = line
            correction = ""
            transcript = ""
            spokenline = SpokenLine(
                linenr, speaker, corpus, chat, correction, transcript)
            spokenline.chat_to_correction()
            spokenline.chat_to_transcript()
            linedict = spokenline.convert_to_dictionary()
            lines_dict['lines'].append(linedict)
        else:
            pass


export_file_path = 'test/testvkampen1.yaml'

with open(export_file_path, 'w') as file:
    yaml.dump(lines_dict, file, default_flow_style=False)


"""
How to process the new_CHAT_utterances_2 file
"""
lines_dict = {'lines': []}

chat_path = 'CHILDES_Replacement_Data/new_CHAT_utterances_2.txt'
with open(chat_path, 'r') as chatfile:
    for line in chatfile:
        line = line.split('\t')
        linenr = line[6].strip()
        speaker = line[5]
        corpus = line[3]
        chat = line[2]
        # remove timestamps from CHAT lines
        chat = re.sub(r'\u0015[0123456789_ ]+\u0015', "", chat)
        correction = line[1]
        transcript = line[0]
        spokenline = spokenline(linenr, speaker, corpus,
                                chat, correction, transcript)
        # spokenline.chat_to_correction()
        # spokenline.chat_to_transcript()
        linedict = spokenline.convert_to_dictionary()
        lines_dict['lines'].append(linedict)

export_file_path = 'CHILDES_Replacement_Data/new_CHAT_utterances.yaml'

with open(export_file_path, 'w') as file:
    yaml.dump(lines_dict, file, default_flow_style=False)

    # https://github.com/UUDigitalHumanitieslab/TrEd-bridge/blob/fc56323cd8921724c23b33c63cfa7400e08d909f/functions.py#L200 Look at this for edit distance
