from clean_test_data import clean_test_data
import yaml
from chamd import ChatReader

reader = ChatReader()
test_data_path = "CHILDES_Replacement_Data/test_output.yaml"  # test data in yaml format
export_file_path = 'CHILDES_Replacement_Data/chamd_test_output.yaml'  # test ouput in yaml format


with open('CHILDES_Replacement_Data/test_output.yaml') as test_data_file:
    test_data = yaml.load(test_data_file, Loader=yaml.FullLoader)['lines']

print("number of entries: {}".format(len(test_data)))

given_file = ['@Participants:	CHI Child']
output_file = ['@Participants:	CHI Child']
for entry in test_data:
    chamd_success = False
    perfect_success = entry['success']
    transcript = entry['transcript']
    correction = entry['correction']
    chat_given = entry['chat_given']
    chat_output = entry['chat_output']

    given_file.append(chat_given)
    output_file.append(chat_output)

given_export_path = 'CHILDES_Replacement_Data/chamd_test_files/given01.cha'
with open(given_export_path, 'w') as file:
    file.write(given_file[0] + '\n')
    for line in given_file[1:]:
        file.write('*CHI:   ' + line + '\n')

given_clean = []
chat = reader.read_file(given_export_path)
for line in chat.lines:
    given_clean.append(line.text)
    
output_export_path = 'CHILDES_Replacement_Data/chamd_test_files/output01.cha'
with open(output_export_path, 'w') as file:
    file.write(output_file[0] + '\n')
    for line in output_file[1:]:
        file.write('*CHI:   ' + line + '\n')

output_clean =[]
chat = reader.read_file(output_export_path)
for line in chat.lines:
    output_clean.append(line.text)


lines_dict = {'lines': []}
success_count = 0

for i in range(len(given_clean)-1):
    success = False
    if given_clean[i] == output_clean[i]:
        success = True
        success_count += 1
    lines_dict['lines'].append({
            'chat_given': given_file[i+1],
            'chat_output': output_file[i+1],
            'clean_given': given_clean[i],
            'clean_output': output_clean[i],
            'success': success
            })

print("Correct output: {}%".format(round((success_count/len(given_clean))*100, 2)))

with open(export_file_path, 'w') as file:
    yaml.dump(lines_dict, file, default_flow_style=False)



