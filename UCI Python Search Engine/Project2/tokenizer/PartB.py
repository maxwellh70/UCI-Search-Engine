import sys
from PartA import count_tokens, tokenize

# Find the number of tokens that appear in both files
# Time complexity: O(n)
def main(args: list[str]):
    """
    :param args:
    :return:
    """
    file1 = args[1]
    file2 = args[2]
    freq_dict1 = count_tokens(tokenize(file1))
    freq_dict2 = count_tokens(tokenize(file2))
    # Find the number of tokens that appear in both files
    count = 0
    for key in freq_dict1:
        if key in freq_dict2:
            count += 1
    print(count)

if __name__ == '__main__':
    main(sys.argv)
