
if __name__ == '__main__':
    test1 = [1, 2, 3, 4, 5]
    test = [3, 4, 5]
    for x in test1:
        if all(x != y for y in test):
            print(x)
