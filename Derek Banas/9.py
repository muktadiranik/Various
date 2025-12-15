class Animal:
    def __init__(self, birth_type="Unknown", appearance="Unknown", blooded="Unknown"):
        self.__birth_type = birth_type
        self.__appearance = appearance
        self.__blooded = blooded

    @property
    def birth_type(self):
        print("birth_type property")
        return self.__birth_type

    @birth_type.setter
    def birth_type(self, value):
        print("birth_type setter")
        self.__birth_type = value

    @property
    def appearance(self):
        print("appearance property")
        return self.__appearance

    @appearance.setter
    def appearance(self, value):
        print("appearance setter")
        self.__appearance = value

    @property
    def blooded(self):
        print("blooded property")
        return self.__blooded

    @blooded.setter
    def blooded(self, value):
        print("blooded setter")
        self.__blooded = value

    def __str__(self):
        return "A {} is {} it is {} it is {}".format(
            type(self).__name__, self.birth_type, self.appearance, self.blooded
        )


class Mammal(Animal):
    def __init__(
        self,
        birth_type="born alive",
        appearance="hair or fur",
        blooded="warm blooded",
        nurse_young=True,
    ):
        Animal.__init__(self, birth_type, appearance, blooded)
        self.__nurse_young = nurse_young

    @property
    def nurse_young(self):
        return self.__nurse_young

    @nurse_young.setter
    def nurse_young(self, value):
        self.__nurse_young = value

    def __str__(self):
        return super().__str__() + " and it nurses its {}".format(self.nurse_young)


class Reptile(Animal):
    def __init__(
        self,
        birth_type="born in an egg or born alive",
        appearance="dry scales",
        blooded="cold blooded",
    ):
        Animal.__init__(self, birth_type, appearance, blooded)
        self.__birth_type = birth_type
        self.__appearance = appearance
        self.__blooded = blooded

    def sum_all(self, *args):
        total = 0
        for arg in args:
            total += arg
        return total


mammal_1 = Mammal("born alive", "hair or fur", "warm blooded", True)
print(mammal_1)

reptile_1 = Reptile("born in an egg or born alive", "dry scales", "cold blooded")
print(reptile_1)

print(reptile_1.sum_all(1, 2, 3, 4, 5))


def get_birth_type(_object):
    print(f"The {_object.birth_type} of birth type is {type(_object).__name__}")


get_birth_type(mammal_1)
get_birth_type(reptile_1)


# ---------- MAGIC METHODS ----------
# Magic methods are surrounded by double underscores
# We can use magic methods to define how operators
# like +, -, *, /, ==, >, <, etc. will work with our
# custom objects

# Magic methods are used for operator overloading
# in Python

# __eq__ : Equal
# __ne__ : Not Equal
# __lt__ : Less Than
# __gt__ : Greater Than
# __le__ : Less Than or Equal
# __ge__ : Greater Than or Equal
# __add__ : Addition
# __sub__ : Subtraction
# __mul__ : Multiplication
# __div__ : Division
# __mod__ : Modulus


class Time:
    def __init__(self, hour=0, minute=0, second=0):
        self.hour = hour
        self.minute = minute
        self.second = second

    def __str__(self):
        return "{:02d}:{:02d}:{:02d}".format(self.hour, self.minute, self.second)

    def __add__(self, other):
        new_time = Time()

        if (self.second + other.second) >= 60:
            self.minute += 1
            new_time.second = (self.second + other.second) - 60
        else:
            new_time.second = self.second + other.second

        if (self.minute + other.minute) >= 60:
            self.hour += 1
            new_time.minute = (self.minute + other.minute) - 60
        else:
            new_time.minute = self.minute + other.minute

        if (self.hour + other.hour) > 24:
            new_time.hour = (self.hour + other.hour) - 24
        else:
            new_time.hour = self.hour + other.hour

        return new_time


time = Time()
print(time)

time_1 = Time(1, 20, 30)
time_2 = Time(24, 41, 30)

print(time_1 + time_2)
