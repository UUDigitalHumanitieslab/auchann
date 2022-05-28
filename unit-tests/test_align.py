from auchann.align_words import align_words


def test_replace():
    transcript_line = "doet zij even de armen wes"
    correction_line = "doet zij even de armen weg"
    expected_chat_line = "doet zij even de armen wes [: weg]"

    assertAlign(transcript_line, correction_line, expected_chat_line)


def test_remove():
    transcript_line = "alleen dit dit"
    correction_line = "alleen dit"
    expected_chat_line = "alleen dit [/] dit"

    assertAlign(transcript_line, correction_line, expected_chat_line)


def test_insert():
    transcript_line = "magge zien"
    correction_line = "mag ik zien"
    expected_chat_line = "magge [: mag] 0ik zien"

    assertAlign(transcript_line, correction_line, expected_chat_line)


def test_repetition():
    transcript_line = "toen kwam hij bij een een weiland"
    correction_line = "toen kwam hij bij een weiland"
    expected_chat_line = "toen kwam hij bij een [/] een weiland"

    assertAlign(transcript_line, correction_line, expected_chat_line)


def test_error_detection():
    transcript_line = "de meisje slaapte thuis"
    correction_line = "het meisje sliep thuis"
    expected_chat_line = "de [: het] [* s:r:gc:art] meisje slaapte [: sliep] [* m] thuis"

    assertAlign(transcript_line, correction_line, expected_chat_line)


def assertAlign(transcript_line: str, correction_line: str, expected_chat_line: str):
    alignment = align_words(transcript_line, correction_line)
    chat_line = str(alignment)
    assert chat_line == expected_chat_line
