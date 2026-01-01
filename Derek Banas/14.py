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

the_string = "A.B.C.  D.E.F. GHI"
print(re.findall(pattern=".\..\..", string=the_string))


the_string = """This is a multiline string,
this is the second line,
this is the third line
"""
print(the_string)

_regex = re.compile("\n")
result = _regex.sub(" ", the_string)
print(result)


the_string = "1 2 3 4 5 11 222 3333 44444 555555"
print(re.findall(pattern="\d", string=the_string))
print(re.findall(pattern="\d{1}", string=the_string))
print(re.findall(pattern="\d{1,3}", string=the_string))
print(re.findall(pattern="\d{5,7}", string=the_string))


# ---------- Matching Any Single Letter or Number ----------
# \w is the same as [a-zA-Z0-9_]
# \W is the same as [^a-zA-Z0-9_]

the_string = "412-555-1212"
if re.search(pattern="\w{3}-\w{3}-\w{4}", string=the_string):
    print("It is a phone number")


# ---------- Matching WhiteSpace ----------
# \s is the same as [\f\n\r\t\v]
# \S is the same as [^\f\n\r\t\v]

the_string = "Jhon Walker"
if re.search(pattern="\w{2,20}", string=the_string):
    print("It is a valid name")

if re.search(pattern="\w{2,20}\s\w{2,20}", string=the_string):
    print("It is a valid full name")

if re.search(pattern="J+", string=the_string):
    print("It is a valid string")


the_string = "db@aol.com m@.com @apple.com db@.com"
print(
    re.findall(pattern="[\w._%+-]{1,20}@[\w.-]{2,20}.[A-Za-z]{2,3}", string=the_string)
)
