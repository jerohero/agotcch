import re

# obsolete?
def take_line_value(line):
    return line.split(" = ")[1].split(" #")[0].split("\n")[0]

def match_date(line):
    return re.match(r"(\d{4})\.(\d{1,2})\.(\d{1,2})", line)

def extract_date_block_year(line):
    match = match_date(line)
    if match:
        year = match.group(1)
        return int(year)
    return 0

def get_nested_value(value):
    return value[value.find('=') + 1 : value.find('}')].strip() # eg. x = { y = z }