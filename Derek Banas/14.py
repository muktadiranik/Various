import re


if re.search("ape", "The ape was at the apex"):
    print("There is an ape")

all_apes = re.findall("ape.", "The ape was at the apex")

for i in all_apes:
    print(i)

for i, j in enumerate(all_apes):
    print(i, j)

the_string = "The ape was at the apex"
for i in re.finditer(pattern="ape.", string=the_string):
    print(i.span(), the_string[i.start() : i.end()])
    print(the_string[i.span()[0] : i.span()[1]])


animal_str = "Cat rat mat fat pat"
all_animals = re.findall(pattern="[crmfp]at", string=animal_str)
print(all_animals)
for i in all_animals:
    print(i)

some_animals = re.findall(pattern="[c-mC-M]at", string=animal_str)
print(some_animals)
for i in some_animals:
    print(i)


some_animals = re.findall(pattern="[^Cr]at", string=animal_str)
print(some_animals)
for i in some_animals:
    print(i)


_regex = re.compile(pattern="[crCR]at")
result = _regex.sub("owl", animal_str)
print(result)


the_string = "Here is \n a new line"
print(the_string)

_regex = re.compile(pattern="\\n")
result = _regex.sub(" ", the_string)
print(result)

print(re.search(pattern="\\n", string=the_string))

the_string = "Here is a \\stuff"
print(re.search(pattern="\\stuff", string=the_string))
print(re.search(pattern="\\\\stuff", string=the_string))
print(re.search(pattern=r"\\stuff", string=the_string))

the_string = "A. B. C.  D. E. F. GHI"
print(re.findall(pattern=".\..\..", string=the_string))
