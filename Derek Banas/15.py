import re


the_string = "cat cats"
_regex = re.compile("[cat]+s?")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)

the_string = "doctor doctors doctor's"
_regex = re.compile(pattern="[doctor]+['s]{0,2}")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)

_regex = re.compile(pattern="[doctor]+['s]*")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)


the_string = """Just some words
and some more\r
and more
"""
_regex = re.compile(pattern="[\w\s]+[\r]?\n")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)

the_string = "<name>Life On Mars</name><name>Freaks and Geeks</name>"
_regex = re.compile(pattern="<name>.*</name>")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)


_regex = re.compile(pattern="<name>.*?</name>")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)


the_string = "ape at the apex"
_regex = re.compile(pattern=r"ape")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)

_regex = re.compile(pattern=r"\bape\b")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)

the_string = "Match everything up to @"
_regex = re.compile(pattern="^.*[^@]")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)

the_string = "@ Get this string"
_regex = re.compile(pattern=r"[^@\s].*$")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)


the_string = """
Ape is big
Turtle is slow
Cheetah is fast
"""
_regex = re.compile(pattern=r"(?m)^.*?\s")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)


the_string = "My number is 412-555-1212"
_regex = re.compile(pattern=r"412-.*")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)

_regex = re.compile(pattern=r"412-(.*)")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)

the_string = "412-555-1212 412-555-1213 412-555-1214"
_regex = re.compile(pattern=r"412-(.{8})")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)

the_string = "My number is 412-555-1212"
_regex = re.compile(pattern=r"412-(.*)-(.*)")
matches = re.findall(pattern=_regex, string=the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)

print(matches[0][0])
print(matches[0][1])
