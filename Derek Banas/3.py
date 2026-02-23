# ---------- MATH MODULE ----------
import math

print("ceil(4.4) = ", math.ceil(4.4))
print("floor(4.4) = ", math.floor(4.4))
print("fabs(-4.4) = ", math.fabs(-4.4))
print("factorial(4) = ", math.factorial(4))
print("fmod(5,4) = ", math.fmod(5, 4))
print("trunc(4.2) = ", math.trunc(4.2))
print("pow(2,2) = ", math.pow(2, 2))
print("sqrt(4) = ", math.sqrt(4))
print("math.e = ", math.e)
print("math.pi = ", math.pi)
print("exp(4) = ", math.exp(4))
print("log(20) = ", math.log(20))
print("log(1000,10) = ", math.log(1000, 10))
print("log10(1000) = ", math.log10(1000))
print("degrees(1.5708) = ", math.degrees(1.5708))
print("radians(90) = ", math.radians(90))


from decimal import Decimal as D

sum = D(0)
sum += D("0.01")
sum += D("0.01")
sum += D("0.01")
sum -= D("0.03")

print("Sum = ", sum)


sample_string = "This is a very important string"

print(sample_string[0])
print(sample_string[-1])
print(sample_string[3 + 5])
print(len(sample_string))
print(sample_string[0:4])
print(sample_string[8:])
print("Green " + "Eggs")
print("Hello " * 5)
num_string = str(4)
for char in sample_string:
    print(char, end="")
print("")
for i in range(0, len(sample_string) - 1, 2):
    print(sample_string[i] + sample_string[i + 1])
print("A =", ord("A"))
print("65 =", chr(65))


normal_string = "This is a normal string"

"""
convert each character to its ASCII value
store them in a new list
"""
shift = 1
secret_string_list = []
for char in normal_string:
    secret_string_list.append(str(ord(char) + shift))

secret_string = ""
for char_code in secret_string_list:
    secret_string += chr(int(char_code))

print(secret_string)

normal_string = ""

for char_code in secret_string_list:
    normal_string += chr(int(char_code) - shift)

print(normal_string)
