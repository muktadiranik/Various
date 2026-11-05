def example_of_yield_and_return():
    for i in range(5):
        yield i


if __name__ == "__main__":
    for value in example_of_yield_and_return():
        print(value)
