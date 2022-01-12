"""""
Created on 12-Jan-2022, 13:30
By Mees van Stiphout
"""""

import sys
from chamd import ChatReader


#reader = ChatReader()
# chat = reader.read_file('example.cha') # or read_string

# for item in chat.metadata:
#     print(item)
# for line in chat.lines:
#     for item in line.metadata:
#         print(item)
#     print(line.text)

def main(args=None):
    if args is None:
        args = sys.argv[1:]







if __name__ == "__main__":
    main()
