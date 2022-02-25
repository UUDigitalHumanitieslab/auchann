import unittest
from auchann.align_words import align_words2


class TestAlign(unittest.TestCase):
    def test_align(self):
        transcript_line = "Sheean is dee man"
        correction_line = "Sheean is de man"

        aligned_tokens = align_words2(transcript_line, correction_line)
        chat_line = ' '.join(object.__str__() for object in aligned_tokens)
        expected_chat_line = "Sheean is dee [: de] man"
        self.assertEqual(chat_line, expected_chat_line)


if __name__ == '__main__':
    unittest.main()
