# ---------- STRING METHODS ----------

rand_string = "   this is an important string   "

rand_string = rand_string.lstrip()
rand_string = rand_string.rstrip()
rand_string = rand_string.strip()

print(rand_string.capitalize())
print(rand_string.upper())
print(rand_string.lower())

a_list = ["Bunch", "of", "random", "words"]
print(" ".join(a_list))

a_list_2 = rand_string.split()

for i in a_list_2:
    print(i)

print("How many is :", rand_string.count("is"))
print("Where is string :", rand_string.find("string"))
print(rand_string.replace("an ", "a kind of "))


# ---------- PROBLEM : ACRONYM GENERATOR ----------
orig_string = "Convert to Acronym"
orig_string = orig_string.upper()
list_of_words = orig_string.split()
for word in list_of_words:
    print(word[0], end="")
print()


# ---------- MORE STRING METHODS ----------
letter_z = "z"
num_3 = "3"
a_space = " "

print("Is z a letter or number :", letter_z.isalnum())
print("Is z a letter :", letter_z.isalpha())
print("Is 3 a number :", num_3.isdigit())
print("Is z a lowercase :", letter_z.islower())
print("Is z a uppercase :", letter_z.isupper())
print("Is space a space :", a_space.isspace())


def is_float(value):
    if float(value):
        return True
    return ValueError("value is not a float")


print(is_float("3.1415"))
print(is_float("3"))


# ---------- PROBLEM : CAESAR'S CIPHER ----------
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
