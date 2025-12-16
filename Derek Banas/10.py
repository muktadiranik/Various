class Sum:
    @classmethod
    def classmethod_get_sum(cls, *args):
        total = 0
        for i in args:
            total += i
        return total

    @staticmethod
    def staticmethod_get_sum(*args):
        total = 0
        for i in args:
            total += i
        return total


sum_1 = Sum()
print(sum_1.classmethod_get_sum(1, 2, 3, 4, 5))
print(sum_1.staticmethod_get_sum(1, 2, 3, 4, 5))


"""
count number of dogs
"""


class Dog:
    number_of_dogs = 0

    def __init__(self, name):
        self.name = name
        Dog.number_of_dogs += 1

    @classmethod
    def classmethod_get_number_of_dogs(cls):
        print(f"There are {cls.number_of_dogs} dogs")
        return cls.number_of_dogs

    @staticmethod
    def staticmethod_get_number_of_dogs():
        print(f"There are {Dog.number_of_dogs} dogs")
        return Dog.number_of_dogs


spot = Dog("spot")
doug = Dog("doug")

print(spot.classmethod_get_number_of_dogs())
print(spot.staticmethod_get_number_of_dogs())


import sum
from sum import get_sum

print(f"get_sum(1, 2, 3, 4, 5): {get_sum(1, 2, 3, 4, 5)}")


# ---------- EXCEPTION HANDLING ----------
# Exceptions are triggered either when an error occurs
# or when you want them to.

# We use exceptions are used to handle errors, execute
# specific code when code generates something out of
# the ordinary, to always execute code when something
# happens (close a file that was opened),

# When an error occurs you stop executing code and jump
# to execute other code that responds to that error

# Let's handle an IndexError exception that is
# triggered when you try to access an index in a list
# that doesn't exist

list_2 = [1, 2, 3, 4, 5]
try:
    print(list_2[5])
except IndexError as e:
    print(f"error: {e}")
except Exception as e:
    print(f"error: {e}")


class AnimalNameError(Exception):
    pass


try:
    name = "Alice:"
    if any(not char.isalpha() for char in name):
        raise AnimalNameError("Name can not contain an non alphabetic character")
except AnimalNameError:
    print("Name can not contain an non alphabetic character")


try:
    num = 6 / 0
except ZeroDivisionError as e:
    print(f"error: {e}")
    print(f"e.args: {e.args}")
else:
    print("No errors were thrown")
finally:
    print("This will always execute")
