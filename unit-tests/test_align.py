import unittest
from auchann.align_words import align_words


class TestAlign(unittest.TestCase):
    def test_replace(self):
        transcript_line = "doet zij even de armen wes"
        correction_line = "doet zij even de armen weg"
        expected_chat_line = "doet zij even de armen wes [: weg]"

        alignment = align_words(transcript_line, correction_line)
        chat_line = ' '.join(str(correction) for correction in alignment.corrections)
        self.assertEqual(chat_line, expected_chat_line)

    def test_remove(self):
        transcript_line = "alleen dit dit"
        correction_line = "alleen dit"
        expected_chat_line = "alleen dit [/] dit"

        alignment = align_words(transcript_line, correction_line)
        chat_line = ' '.join(str(correction) for correction in alignment.corrections)
        self.assertEqual(chat_line, expected_chat_line)

    def test_insert(self):
        transcript_line = "magge zien"
        correction_line = "mag ik zien"
        expected_chat_line = "magge [: mag] 0ik zien"

        alignment = align_words(transcript_line, correction_line)
        chat_line = ' '.join(str(correction) for correction in alignment.corrections)
        self.assertEqual(chat_line, expected_chat_line)




if __name__ == '__main__':
    unittest.main()
