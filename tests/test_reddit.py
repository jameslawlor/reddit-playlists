from functions.reddit import trim_wikipage


def test_trim_wikipage():
    test_wiki_input = [
        "#Subreddits by genre \t\t",
        "## Genre 1",
        "geaiealnea /r/test1 egaoingeonag",
        "* /r/test2 blah",
        "## Genre 2",
        "* /r/test3 - description",
        "#Multi-genre & community subreddits blah blah",
        "this should be ignored",
    ]

    expected_output = [
        "## Genre 1",
        "geaiealnea /r/test1 egaoingeonag",
        "* /r/test2 blah",
        "## Genre 2",
        "* /r/test3 - description",
    ]
    test_wiki_output = trim_wikipage(test_wiki_input)
    assert test_wiki_output == expected_output
