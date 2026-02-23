# example of module with classes
class Animal:
    def __init__(self):
        self.name = "Animal"
        self.age = 0
        self.weight = 0

    def eat(self):
        print("eat")

    # Define a property
    @property
    def name(self):
        print("name getter")
        return self.__name

    @name.setter
    def name(self, value):
        print("name setter")
        self.__name = value

    @classmethod
    def sleep(cls):
        print(f"cls.__name__: {cls.__name__}")
        print("sleep")


class Mammal(Animal):
    def __init__(self):
        super().__init__()
        self.name = "Mammal"
        self.age = 21
        self.weight = 150

    def talk(self):
        print("talk")


mammal = Mammal()
print(mammal.name)
mammal.talk()
mammal.eat()
mammal.sleep()


def calc_tax():
    pass


def calc_shipping():
    pass
