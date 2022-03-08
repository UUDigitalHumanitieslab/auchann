import yaml
import re

lines_dict = {'lines': []}
chat_path = 'CHILDES_Replacement_Data/new_CHAT_utterances_2.txt'
with open(chat_path, 'r') as chatfile:
    i = 0
    for line in chatfile:
        if i > 1000:
            break
        else:
            aux = line.split('\t')
            line = aux
            linenr = line[6].strip()
            speaker = line[5]
            corpus = line[3]
            chat = line[2]
            correction = line[1]
            transcript = line[0]
            
            # CHAT line cleanup 
            chat = re.sub(r'\u0015[0123456789_ ]+\u0015', "", chat)  # remove timestamp glitch
            chat = re.sub(r'\u21AB[a-zA-Z0-9]*\u21AB', "", chat)  # remove left-arrow symbol glitch
            chat = re.sub(r'(\([a-zA-Z0-9.]*\)\ )', "", chat)  # remove pauses (e.g. '(2.3)')
            chat = chat.replace("[*s]", "")
            chat = chat.replace(" [*m]", "")
            chat = chat.replace(" [*gram]", "")
            

            linedict = {
                'content':{
                    'CHAT': chat.strip(" "),  # delete trailing spaces
                    'correction': correction,
                    'transcript': transcript
                },
                'meta':{
                    'corpus':corpus,
                    'line': linenr,
                    'speaker': speaker
                }
            }
        lines_dict['lines'].append(linedict)
        i += 1



export_file_path = 'CHILDES_Replacement_Data/test_data_abdridged.yaml'

with open(export_file_path, 'w') as file:
    yaml.dump(lines_dict, file, default_flow_style=False)
