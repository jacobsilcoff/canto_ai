import pycantonese


def get_accurate_jyutping(text):
    """
    Converts Cantonese characters to Jyutping using pycantonese.
    Returns a string like 'nei5 hou2'.
    """
    # segments the text and returns a list of (word, jyutping) tuples
    characters = pycantonese.characters_to_jyutping(text)

    # The library returns a list of tuples like [('nei', '5'), ('hou', '2')]
    # We join them back into a string.
    jyutping_str = " ".join([f"{char[1]}" for char in characters])

    return jyutping_str


# Test it
if __name__ == "__main__":
    print(get_accurate_jyutping("其實做醫生好辛苦"))
    # Output: kei4 sat6 zou6 ji1 sang1 hou2 san1 fu2