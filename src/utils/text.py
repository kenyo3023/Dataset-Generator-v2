import re
# import json

def match_and_parse_plain_text(text:str, pattern:str) -> str:
    """Searches for a pattern in the input text and returns the matched content.

    Args:
        text (str): The input text where the pattern will be searched.
        pattern (str): The regular expression pattern to match.

    Returns:
        str: The matched content if the pattern is found; otherwise, None.
    
    Notes:
        The function uses regular expressions to search the input text for the given pattern.
        If a match is found, the matched content is returned. If no match is found, None is returned.
        Currently, the function only returns the matched group and does not handle the case of extracting 
        and parsing JSON data (this part is commented out for future development).
    """
    pattern = rf'{pattern}'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        # try:
        #     json_str = match.group(1)
        #     messages = json.loads(json_str)
        #     return messages
        # except Exception as e:
        #     # return None # TODO
        #     raise e
        return match.group(1)
    else:
        print("No match found.")
        return None # TODO