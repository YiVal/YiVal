from typing import List, Union
from PIL.PngImagePlugin import PngImageFile
from fuzzywuzzy import fuzz

def fuzzy_match_util(
    generated: str, expected: Union[str, List[PngImageFile]], threshold: int = 80
) -> bool:
    """
    Matches the generated string with the expected answer(s) using fuzzy
    matching.

    Args:
        generated (str): The generated string.
        expected (str): The expected answer(s). Can be a string or list of
        strings.
        threshold (int, optional): The threshold for fuzzy matching. Defaults
        to 80.

    Returns:
        int: Returns 1 if there's a match, 0 otherwise.
    """
    if isinstance(expected, str):
        if fuzz.ratio(generated, expected) > threshold:
            return True
    elif isinstance(expected, list):
        return False
    else:
        return False
        
