import yaml
import re

def clean_test_data(chat_path: str, export_file_path: str, filelength=1000, max_s_length=40):
    lines_dict = {'lines': []}
    with open(chat_path, 'r') as chatfile:
        i = 0
        for line in chatfile:
            if i >= filelength:
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

                """
                This test does not consider strings longer than 8 words due to runtime issues
                """
                if len(transcript.split()) > max_s_length:
                    pass
                else:                
                    # CHAT line cleanup 
                    chat = re.sub(r'\u0015[0123456789_ ]+\u0015', "", chat)  # remove timestamp glitch
                    chat = re.sub(r'\u21AB[a-zA-Z0-9]*\u21AB', "", chat)  # remove left-arrow symbol glitch
                    chat = re.sub(r'(\([a-zA-Z0-9.]*\)\ )', "", chat)  # remove pauses (e.g. '(2.3)')
                    chat = chat.replace("[*s]", "")  # remove error markers
                    chat = chat.replace(" [*m]", "")
                    chat = chat.replace(" [*gram]", "")
                    chat = chat.replace("&die", "<die> [//]")  # annotation disagreement: do not use '&die'
                    if re.search(r"\[:[a-zA-Z0-9]", chat):  # add a space in corrections where there is none
                        chat = chat.replace("[:", "[: ")
                    

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

    with open(export_file_path, 'w') as file:
        yaml.dump(lines_dict, file, default_flow_style=False)


# Example:
chat_path = 'CHILDES_Replacement_Data/new_CHAT_utterances_2.txt'
export_file_path = 'CHILDES_Replacement_Data/test_data_long.yaml'
clean_test_data(chat_path, export_file_path, 10000, 8)
