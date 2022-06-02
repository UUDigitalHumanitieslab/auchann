import unittest
from auchann.correct_parenthesize import correct_parenthesize


class TestParenthesize(unittest.TestCase):
    def test_parenthesize(self):
        data = [("n", "een", "(ee)n"),
                ("wee", "twee", "(t)wee"),
                ("gee", "geen", "gee(n)"),
                ("ga-ga-gaan", "gaan", "\u21ABga-ga\u21ABgaan"),
                ("es", "eens", "e(en)s"),
                ("feliteerd", "gefeliciteerd", "(ge)feli(ci)teerd"),
                ("feliteer", "gefeliciteerd", "(ge)feli(ci)teer(d)")]

        for original, correction, expected in data:
            actual = correct_parenthesize(original, correction)
            self.assertEqual(actual, expected,
                             f"{original} \u2192 {correction}")


if __name__ == '__main__':
    unittest.main()
