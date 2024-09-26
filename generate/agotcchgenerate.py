import os
import json
from util import file, text
import textwrap
from birth_effects import generate_birth_effects
from story_cycles import generate_story_cycles
from script_values import generate_script_values
from dummy_characters import generate_dummy_characters
from character import process_character
from lookups import *

path = "C:/Users/Jeroen/Documents/Paradox Interactive/Crusader Kings III/mod/agotcch/generate"

def process_lines():
    current_year_block = 0
    character_start_index = 0

    characters = {}

    for i, line in enumerate(lines):
        if not line or line[0] == '#':
            continue
        
        is_line_character_name = "\tname = " in line

        canon_statuses = ["canon_status_canon", "canon_status_semicanon"] # ... canon_status_mentioned
        is_line_canon_child = any(status in line for status in canon_statuses)

        if is_line_character_name:
            character_start_index = i

        if is_line_canon_child:
            character = process_character(lines, character_start_index)

            if character is None or character["skipped"] is True:
                continue

            has_mother = character["mother"] != ""
            has_father = character["father"] != "" or character["real_father"] != ""

            # Skip characters without parents
            if not has_mother and not has_father:
                continue
            elif not has_mother:
                # TODO handle characters with only a father
                continue
            elif not has_father:
                # TODO handle characters with only a mother (eg Maege Mormont's children)
                continue
            
            characters[character["id"]] = character
            print(f'\rProcessed: {character["id"]} - {character["name"]["primary"]}', end='\x1b[2K')

    print(f'\r{len(characters)} characters processed', end='')
    
    fathers, mothers = find_ancestries(characters)

    # with open(path + '/output/common/story_cycles/agot_canon_children_story_cycles.txt', 'w') as f:
    with open('C:/Users/Jeroen/Documents/GitHub/agot/common/story_cycles/agot_canon_children_story_cycles.txt', 'w') as f:
        f.write(generate_story_cycles(characters, fathers, mothers))

    # with open(path + '/output/common/scripted_effects/00_agot_scripted_effects_canon_children_birth.txt', 'w') as f:
    with open('C:/Users/Jeroen/Documents/GitHub/agot/common/scripted_effects/00_agot_scripted_effects_canon_children_birth.txt', 'w') as f:
        f.write(generate_birth_effects(characters, fathers, mothers))

    # with open(path + '/output/common/script_values/00_agot_canon_children_values.txt', 'w') as f:
    with open('C:/Users/Jeroen/Documents/GitHub/agot/common/script_values/00_agot_canon_children_values.txt', 'w') as f:
        f.write(generate_script_values(characters))

    # with open(path + '/output/history/characters/canon_children_dummy_characters.txt', 'w') as f:
    with open('C:/Users/Jeroen/Documents/GitHub/agot/history/characters/agot_canon_children_dummy_characters.txt', 'w') as f:
        f.write(generate_dummy_characters(characters))

    with open('C:/Users/Jeroen/Documents/GitHub/agot/common/scripted_triggers/agot_scripted_triggers_canon_characters.txt', 'w') as f:
        f.write(generate_triggers(characters))
        
    with open('CC:/Users/Jeroen/Documents/GitHub/agot/common/traits/00_agot_canon_children_traits.txt', 'w') as f:
        f.write(generate_traits(characters))


# folder_path = path + '/characters/small'
folder_path = 'C:/Users/Jeroen/Documents/GitHub/agot/history/characters'
excluded_files = ['00_agot_char_dragons.txt']
lines = file.read_text_files_to_lines(folder_path, excluded_files)

process_lines()
