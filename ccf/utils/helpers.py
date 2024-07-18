from typing import List

def containsAny(substrings: List[str], string_to_search: str) -> bool:
    return any(substring in string_to_search for substring in substrings)


def startsWith(source_string: str, search_string: str, position: int = 0) -> bool:
    """
    Returns true if the sequence of elements of search_string is the same as the corresponding
    elements of source_string starting at the given position. Otherwise returns false.

    :param source_string: The string to search within.
    :param search_string: The string to search for.
    :param position: The position to start searching from.
    :return: True if the source_string starts with search_string at the given position, False otherwise.
    """
    return source_string.startswith(search_string, position)

