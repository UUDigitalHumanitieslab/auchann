from auchann.align_words import align_words

import yaml

test_data_path = "CHILDES_Replacement_Data/test_data_abdridged.yaml"
lines_dict = {'lines': []}


with open(test_data_path) as test_data_file:
    test_data = yaml.load(test_data_file, Loader=yaml.FullLoader)['lines']

test_data_short = []
for entry in test_data:
    """
    This test does not consider strings longer than 8 words due to runtime issues
    """
    if len(entry['content']['transcript'].split()) > 8:
        pass
    else:
        test_data_short.append(entry)

success_count = 0
for entry in test_data_short:
    success = False
    transcript = entry['content']['transcript']
    correction = entry['content']['correction']
    chat_given = entry['content']['CHAT']

    alignment = align_words(transcript, correction)
    chat_output = ' '.join(str(corrected) for corrected in alignment.corrections)

    if chat_given == chat_output:
        success = True
        success_count += 1

    lines_dict['lines'].append({
        'success': success,
        'transcript':transcript,
        'correction': correction,
        'chat_given': chat_given,
        'chat_output': chat_output,
        })

print("number of entries: {}".format(len(test_data_short)))
print("Correct output: {}%".format(round((success_count/len(test_data_short))*100, 2)))


export_file_path = 'CHILDES_Replacement_Data/test_output.yaml'

with open(export_file_path, 'w') as file:
    yaml.dump(lines_dict, file, default_flow_style=False)