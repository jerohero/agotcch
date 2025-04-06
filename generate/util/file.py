import os

def read_text_file_to_lines(file_path):
    lines = []
    if os.path.isfile(file_path) and file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    return lines

def read_text_files_to_lines(folder_path, excluded_files=[]):
    lines = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt') and filename not in excluded_files:
            lines.extend(read_text_file_to_lines(file_path))
    return lines
