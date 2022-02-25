import unittest
from auchann.align_words import align_words2


class TestAlign(unittest.TestCase):
    def test_replace(self):
        transcript_line = "Sheean is dee man"
        correction_line = "Sheean is de man"
        expected_chat_line = "Sheean is dee [: de] man"

        aligned_tokens = align_words2(transcript_line, correction_line)
        chat_line = ' '.join(object.__str__() for object in aligned_tokens)
        expected_chat_line = "Sheean is dee [: de] man"
        self.assertEqual(chat_line, expected_chat_line)

    def test_remove(self):
        transcript_line = "Sheean is dee beste man"
        correction_line = "Sheean is de man"
        expected_chat_line = "Sheean is dee [: de] <beste> [///] man"

        aligned_tokens = align_words2(transcript_line, correction_line)
        chat_line = ' '.join(object.__str__() for object in aligned_tokens)
        self.assertEqual(chat_line, expected_chat_line)

    def test_insert(self):
        transcript_line = "Sheean is dee man"
        correction_line = "Sheean is de beste man"
        expected_chat_line = "Sheean is dee [: de] 0beste man"

        aligned_tokens = align_words2(transcript_line, correction_line)
        chat_line = ' '.join(object.__str__() for object in aligned_tokens)
        self.assertEqual(chat_line, expected_chat_line)




if __name__ == '__main__':
    unittest.main()
