from codeforlife.helper import get_names


def test_get_names():
    assert get_names() == [
        "Stefan\n",
        "Kamil\n",
        "Florian\n",
        "Laura\n",
        "Chris\n",
        "Duncan\n",
    ]
