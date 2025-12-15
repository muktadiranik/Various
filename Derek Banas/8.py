class Animal:
    def __init__(self, name, height, weight):
        self.name = name
        self.height = height
        self.weight = weight

    def run(self):
        print(f"{self.name} runs")

    def sleep(self):
        print(f"{self.name} sleeps")

    def eat(self):
        print(f"{self.name} eats")


class Dog(Animal):
    def __init__(self, name, height, weight, sound):
        self.sound = sound
        super().__init__(name, height, weight)

    def bark(self):
        print(f"{self.name} barks")


dog_1 = Dog("Buddy", 10, 20, "Woof")
dog_1.run()
dog_1.sleep()
dog_1.eat()
dog_1.bark()


class Square:
    def __init__(self, height="0", width="0"):
        self.height = height
        self.width = width

    @property
    def height(self):
        print("property height")
        return self.__height

    @height.setter
    def height(self, value):
        if int(value) < 0:
            print("Height cannot be less than 0")
        elif not value.isdigit():
            print("Height cannot be a string")
        else:
            self.__height = value

    @property
    def width(self):
        print("property width")
        return self.__width

    @width.setter
    def width(self, value):
        if int(value) < 0:
            print("Width cannot be less than 0")
        elif not value.isdigit():
            print("Width cannot be a string")
        else:
            self.__width = value

    def get_area(self):
        return int(self.__height) * int(self.__width)


square = Square(height="2", width="5")
print(square.height, square.width)
print(square.get_area())
