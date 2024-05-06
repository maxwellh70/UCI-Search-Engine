import itertools

token_dict = {i: i % 2 for i in range(10704)}

length = len(token_dict)
for i in range(0, length, 1000):
    params = []
    for token, token_object in itertools.islice(token_dict.items(), i, i + 1000):
        print(token, end=" ")
    print()
    print()