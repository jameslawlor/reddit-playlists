from functions.reddit import trim_wikipage


def get_test_wiki_input():
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
    return test_wiki_input


def test_trim_wikipage():

    expected_output = [
        "## Genre 1",
        "geaiealnea /r/test1 egaoingeonag",
        "* /r/test2 blah",
        "## Genre 2",
        "* /r/test3 - description",
    ]

    genre_section_start_regex = "#Subreddits by genre.*"
    genre_section_end_regex = "#Multi-genre & community subreddits.*"

    test_wiki_input = get_test_wiki_input()
    test_wiki_output = trim_wikipage(
        test_wiki_input, genre_section_start_regex, genre_section_end_regex
    )
    assert test_wiki_output == expected_output
