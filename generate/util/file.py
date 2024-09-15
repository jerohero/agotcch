import os

def read_text_files_to_lines(folder_path):
    lines = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                lines.extend(file.readlines())
    return lines