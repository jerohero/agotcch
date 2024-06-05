def take_line_value(line):
    return line.split(" = ")[1].split(" #")[0].split("\n")[0]