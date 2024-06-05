import os

def read_text_files_to_lines(folder_path):
    lines = []
    # Sprawdź każdy plik w folderze
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Upewnij się, że plik jest plikiem tekstowym
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            # Otwórz plik i dodaj jego linie do listy
            with open(file_path, 'r', encoding='utf-8') as file:
                lines.extend(file.readlines())
    return lines