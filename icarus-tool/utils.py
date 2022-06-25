def extract(sentence: str, sep: str = " ", reverse: bool = False) -> tuple[str, str]:
    """
    Use a separator to divide entries into next entry and remaining entries.
    Note that, unnecessary whitespaces will be removed during the process.
    """

    # Remove any extra whitespace from the input.
    word = " ".join(sentence.split())
    sentence = ""
    if sep in word and not reverse:
        index = word.find(sep)
        sentence = word[index + len(sep):]
        word = word[:index]
    if sep in word and reverse:
        index = word.rfind(sep)
        sentence = word[:index]
        word = word[index + len(sep):]
    return word, sentence
