from functions.reddit import (
    trim_wikipage,
    parse_wikipage,
    does_submission_match_track_format,
    get_artist_and_track_from_submission,
)


def get_test_wiki_input():
    test_wiki_input = [
        "#Subreddits by genre \t\t",
        "##Genre 1",
        "geaiealnea /r/test1 egaoingeonag",
        "* /r/test2 blah",
        "##Genre 2",
        "* /r/test3 - description",
        "#Multi-genre & community subreddits blah blah",
        "this should be ignored",
    ]
    return test_wiki_input


def test_trim_wikipage():

    expected_output = [
        "##Genre 1",
        "geaiealnea /r/test1 egaoingeonag",
        "* /r/test2 blah",
        "##Genre 2",
        "* /r/test3 - description",
    ]

    genre_section_start_regex = "#Subreddits by genre.*"
    genre_section_end_regex = "#Multi-genre & community subreddits.*"

    test_wiki_input = get_test_wiki_input()
    test_wiki_output = trim_wikipage(
        test_wiki_input, genre_section_start_regex, genre_section_end_regex
    )
    assert test_wiki_output == expected_output

    expected_output_2 = {
        "test1": {"genre": "Genre 1"},
        "test2": {"genre": "Genre 1"},
        "test3": {"genre": "Genre 2"},
    }
    genre_regex = "##.*"
    subreddit_regex = ".*/r/.*"
    test_parse_wikipage_output = parse_wikipage(
        test_wiki_output, genre_regex, subreddit_regex
    )
    print(test_parse_wikipage_output)
    assert test_parse_wikipage_output == expected_output_2


def test_does_submission_match_track_format():

    test_inputs = [
        (
            "https://open.spotify.com/album/2NRBI2mvyZIYpHMEcDmN6A?si=qOLtbUCpRWaHqAnfauSu8w&utm_source=copy-link",
            "Said The Sky - Sentiment (LP)",
        ),
        (
            "https://open.spotify.com/album/6UEOL9j71DS5c7yvHV5xUW?si=eGVCum_kR-Wemhy5lTP3tQ&utm_source=copy-link",
            "Trivecta - Sail Away (feat. Jay Mason)",
        ),
        (
            "https://open.spotify.com/album/3wsZl7oZ9obf53nPRj6FaA?si=FzJSiZ0hQJepsWY2MB7I_Q&utm_source=copy-link",
            "Louis The Child - Blow The Roof (with Kasbo & EVAN GIIA)",
        ),
        (
            "https://open.spotify.com/track/5mfwPQqeoP8jzGJCHwM3iF?si=55d11bfb70cb41b3",
            "G Jones X EPROM - On My Mind",
        ),
        ("https://reddit.com", "G Jones X EPROM - On My Mind"),
        ("https://blah.net", "G Jones X EPROM - On My Mind"),
        ("https://missing.com", "G Jones X EPROM - On My Mind"),
    ]
    expected_outputs = [
        True,
        True,
        True,
        True,
        False,
        False,
        False,
    ]
    post_regex_pattern = "[-—]+"
    allowed_domains = ["spotify", "youtu", "soundcloud"]

    for (input, expected_output) in zip(test_inputs, expected_outputs):
        (submission_url, submission_title) = input
        assert expected_output == does_submission_match_track_format(
            submission_url, submission_title, post_regex_pattern, allowed_domains
        )


def test_get_artist_and_track_from_submission():
    test_inputs = [
        "[Bahhh]",
        "[BLAH] Artist1 - Track1",
        "[BLAH] Artist2 - Track2",
        "[BLAH] Artist3 --- Track3",
        "[BLAH][BLAH] Artist4 ---- Track4 (Feat. Blah)",
        "Artist5 ---- Track5 (Feat. Blah)",
        "[BLAH][BLAH] Artist4 / Track4 (Feat. Blah)",
        "Artist4 + Track4",
        "Artist4 ———— Track4",
        "Artist4 — Track4",
    ]
    expected_outputs = [
        (None, None),
        ("Artist1", "Track1"),
        ("Artist2", "Track2"),
        ("Artist3", "Track3"),
        ("Artist4", "Track4"),
        ("Artist5", "Track5"),
        (None, None),
        (None, None),
        ("Artist4", "Track4"),
        ("Artist4", "Track4"),
    ]

    post_regex_pattern = "[-—]+"

    for (input, expected_output) in zip(test_inputs, expected_outputs):
        assert expected_output == get_artist_and_track_from_submission(
            input, post_regex_pattern
        )
