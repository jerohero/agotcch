import os

def read_text_file_to_lines(file_path):
    lines = []
    if os.path.isfile(file_path) and file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    return lines

def read_text_files_to_lines(folder_path, excluded_files=[], only_files=[]):
    lines = []
    for filename in os.listdir(folder_path):
        if only_files and filename not in only_files:
            continue
        if excluded_files and filename in excluded_files:
            continue
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            lines.extend(read_text_file_to_lines(file_path))
    return lines
