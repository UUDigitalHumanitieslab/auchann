from auchann.align_words import AlignmentSettings, align_words, align_split


def test_replace():
    transcript_line = "doet zij even de armen wes"
    correction_line = "doet zij even de armen weg"
    expected_chat_line = "doet zij even de armen wes [: weg]"

    assert_align(transcript_line, correction_line, expected_chat_line)


def test_remove():
    transcript_line = "alleen dit dit"
    correction_line = "alleen dit"
    expected_chat_line = "alleen dit [/] dit"

    assert_align(transcript_line, correction_line, expected_chat_line)


def test_insert():
    data = [
        ("magge zien", "mag ik zien", "magge [: mag] 0ik zien"),
        ("dit is huis", "dit is het huis", "dit is 0het huis"),
        ("dit is huis ja", "dit is het huis ja", "dit is 0het huis ja")
    ]

    for transcript_line, correction_line, expected_chat_line in data:
        assert_align(transcript_line, correction_line, expected_chat_line)


def test_repetition():
    transcript_line = "toen kwam hij bij een een weiland"
    correction_line = "toen kwam hij bij een weiland"
    expected_chat_line = "toen kwam hij bij een [/] een weiland"

    assert_align(transcript_line, correction_line, expected_chat_line)


def test_error_detection():
    transcript_line = "de meisje slaapte thuis"
    correction_line = "het meisje sliep thuis"
    expected_chat_line = "de [: het] [* s:r:gc:art] meisje slaapte [: sliep] [* m] thuis"

    assert_align(transcript_line, correction_line, expected_chat_line)


def test_split():
    data = [
        ("was", "wat is", ["wa", "s"]),
        ("lama", "laat maar", ["la", "ma"]),
        ("goege", "goede morgen", ["goe", "ge"]),
        ("hoest", "hoe is het", ["hoe", "s", "t"]),
        # no trailing characters
        ("wast", "wat is", []),
        ("hoest", "hoe is", []),
    ]

    for transcript_line, correction_line, expected in data:
        splits = align_split(transcript_line, correction_line.split(' '))
        assert splits == expected


def test_multi_word():
    data = [
        ("das wel vreemd", "dat is wel vreemd", "da(t) (i)s wel vreemd"),
        ("was de dat nou?", "wat is de dat nou?", "wa(t) (i)s de dat nou?"),
        ("g ebt dak weet nie oe goe gedaan !",
         "ge hebt dat ik weet niet hoe goed gedaan !",
         "g(e) (h)ebt da(t) (i)k weet nie(t) (h)oe goe(d) gedaan !")
    ]

    for transcript_line, correction_line, expected_chat_line in data:
        assert_align(transcript_line, correction_line, expected_chat_line)


def assert_align(transcript_line: str, correction_line: str, expected_chat_line: str):
    settings = AlignmentSettings()
    def detect_error(original: str, correction: str):
        if original == "slaapte" and correction == "sliep":
            return 1, "m"
        else:
            return 0, None
    settings.detect_error = detect_error

    alignment = align_words(transcript_line, correction_line, settings)
    chat_line = str(alignment)
    assert chat_line == expected_chat_line
