from module import calc_shipping, calc_tax, Animal
import module
import module_2
import sys

animal = Animal()
animal.sleep()
animal.name = "Derek"
print(animal.name)
calc_tax()
calc_shipping()
module.calc_shipping()

print(sys.path)
for path in sys.path:
    print(path)


for name in dir(module):
    print(name)

print(module_2, __name__)
