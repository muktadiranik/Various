import re


the_string = "1. Dog 2. Cat 3. Turtle"
_regex = re.compile(r"\d\.\s(Dog|Cat)")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)


the_string = "12345 12345-1234 1234 12346-333"
_regex = re.compile("(\d{5}-\d{4}|\d{5}\s)")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)


match = re.search(r"\d{2}", "The chicken weighed 13 lbs")
print("Match :", match.group())
print("Span :", match.span())
print("Match :", match.start())
print("Match :", match.end())


the_string = "December 21 1974"
_regex = re.compile(r"^(?P<month>\w+)\s(?P<day>\d+)\s(?P<year>\d+)")
matches = re.search(_regex, the_string)
print("Month :", matches.group("month"))
print("Day :", matches.group("day"))
print("Year :", matches.group("year"))


the_string = "d+b@aol.com a_1@yahoo.co.uk A-100@m-b.INTERNATIONAL"
_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)


the_string = (
    "14125551212 4125551212 (412)5551212 412 555 1212 412-555-1212 1-412-555-1212"
)
# _regex = re.compile(
#     r"""
#     (               # Start of main group
#         (1?)        # Optional country code (1)
#         ([- ]?)     # Optional separator (space or dash)
#         (\()?       # Optional opening parenthesis
#         (\d{3})     # Area code (3 digits)
#         ([)-]| |\)-|\) )?  # Optional separator (closing parenthesis, space, or dash)
#         (\d{3})     # Exchange code (3 digits)
#         ([- ])?     # Optional separator (space or dash)
#         (\d{4})     # Line number (4 digits)
#     )               # End of main group
# """,
#     re.VERBOSE,
# )
_regex = re.compile(r"((1?)(-| ?)(\()?\d{3}(\)|-| |)-?\d{3}-?\d{4})")
matches = re.findall(_regex, the_string)
print("Matches :", len(matches))
for i in matches:
    print(i)
