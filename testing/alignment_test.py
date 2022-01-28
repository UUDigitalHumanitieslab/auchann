from auchann import align_words



transcript_line = "k heb da nooit nie xx gehad"
correction_line = "ik heb dat nooit niet gehad"

transdict, corrdict = align_words.align_words(transcript_line, correction_line)

print("TRANSCRIPT\t\t MATCH")
for key in transdict:
    print(key, "\t\t", transdict[key])

print("\nCORRECTION\t\t MATCH")

for key in corrdict:
    print(key, "\t\t", corrdict[key])

print("\n")