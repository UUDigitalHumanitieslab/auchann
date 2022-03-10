from auchann.align_words import align_words
from auchann.clean_test_data import clean_test_data
import time
import yaml

start_time = time.time()


chat_data_path = "CHILDES_Replacement_Data/new_CHAT_utterances_2.txt"  # cha or txt input
test_data_path = "CHILDES_Replacement_Data/test_data_abridged.yaml"  # test data in yaml format
export_file_path = 'CHILDES_Replacement_Data/test_output.yaml'  # test ouput in yaml format

n_entries = 100
max_sentence_length = 8
clean_test_data(chat_data_path, test_data_path, n_entries, max_sentence_length)  # creates a yaml file from the chat data at test_data_path

lines_dict = {'lines': []}  # dict that eventually contains all output


with open(test_data_path) as test_data_file:
    test_data = yaml.load(test_data_file, Loader=yaml.FullLoader)['lines']


print("number of entries: {}".format(len(test_data)))

success_count = 0
counter =  0
for entry in test_data:
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
    counter += 1
    if counter/len(test_data) in [0.25, 0.5, 0.75, 1]:
        print("{}% done".format(round(counter/len(test_data)*100),2))

print("Correct output: {}%".format(round((success_count/len(test_data))*100, 2)))



with open(export_file_path, 'w') as file:
    yaml.dump(lines_dict, file, default_flow_style=False)

print("Test took {} seconds".format(round(time.time() - start_time, 3)))