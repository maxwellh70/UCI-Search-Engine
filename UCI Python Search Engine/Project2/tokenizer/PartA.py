import sys
# Time complexity: O(n)
def tokenize(string_content: str) -> list[str]:
    """
    Tokenize this file and returns a list of token. A token is a sequence of alphanumeric characters, independent of
    capitalization (so Apple, applE and aPPle are the same token "apple").
    :param file_name: the name of the file to be tokenized
    :return: a list of tokens
    """
    # Tokenize the file
    token_list = []
    content = string_content.lower()
    token = ''
    for char in content:
        if char.isalnum() and char.isascii():
            token += char
        else:
            if token:
                token_list.append(token)
                token = ''
    if token:
        token_list.append(token)
    return token_list


# Time complexity: O(n)
def count_tokens(token_list: list[str]) -> dict[str, int]:
    """
    :param token_list: a list of tokens
    :return: a dictionary with the frequency of each token
    """
    freq_dict = {}
    for token in token_list:
        freq_dict[token] = freq_dict.get(token, 0) + 1
    return freq_dict


# Time complexity: O(nlogn) due to sorting
def print_dict(d: dict[str, int]) -> None:
    """
    :param d: a dictionary
    :return: None
    """
    # Sort the frequency dictionary by value in descending order and break ties by sorting by key in ascending order
    freq_dict = sorted(d.items(), key=lambda x: (-x[1], x[0]))
    for key, value in freq_dict:
        print(f'{key}\t{value}')

def main(args: list[str]):
    """
    :param args: a list of command line arguments
    :return: None
    """
    # Read a file from the command line
    if len(args) > 2:
        return
    freq_dict = count_tokens(tokenize(args[1]))
    print_dict(freq_dict)


if __name__ == '__main__':
    main(sys.argv)
