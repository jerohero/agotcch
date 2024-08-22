import os
import json
from util import file, text
import textwrap
from birth_effects import generate_birth_effects
from story_cycles import generate_story_cycles
from lookups import *

personality_traits_dumpster = [
    "lustful","chaste","gluttonous","temperate","greedy","generous","lazy","diligent","wrathful","calm","patient","impatient","arrogant",
    "humble","deceitful","honest","craven","brave","shy","gregarious","ambitious","content","arbitrary","just","cynical","zealous",
    "paranoid","trusting","compassionate","callous","sadistic","stubborn","fickle","eccentric","vengeful","forgiving",
    "honorable","authoritative","rude","ruthless"
]
childhood_personality_traits_dumpster = [
    "curious","bossy","pensive","rowdy","charming"
]
physical_traits_dumpster = [
    "beauty_bad_1","beauty_bad_2","beauty_bad_3","beauty_good_1","beauty_good_2","beauty_good_3",
    "intellect_bad_1","intellect_bad_2","intellect_bad_3","intellect_good_1","intellect_good_2","intellect_good_3",
    "physique_bad_1","physique_bad_2","physique_bad_3","physique_good_1","physique_good_2","physique_good_3",
    "pure_blooded","fecund","strong","shrewd","clubfooted","hunchbacked","lisping","stuttering","dwarf","giant",
    "inbred","weak","dull","impotent","spindly","scaly","albino","wheezing","bleeder","infertile"
]

def init_character():
    return {
        "id": "",
        "name": {
            "primary": "",
            "alt": ""
        },
        "birth": 0,
        "is_female": False,
        "house": "",
        "father": "",
        "real_father": "",
        "mother": "",
        "dna": "",
        "sexuality": "",
        "employer:": "",
        "traits": {
            "inherited": [],
            "inactive": [],
            "childhood": "",
            "education": []
        },
        "flags": [],
        "is_bastard": False,
        "guardian": {
            "primary": {
                "id": ""
            },
            "alt": {
                "id": ""
            },
            "use_liege_for_heir": False,
            "convert_culture": False,
            "convert_religion": False
        },
        "nickname": "",
        "on_birth": "",
        "config": { "prevent_pregnancy": False }
    }

def get_nested_value(value):
    return value[value.find('=') + 1 : value.find('}')].strip() # eg. x = { y = z }

def process_lines():
    is_reading_character = False
    current_year_block = 0

    characters = {}

    for i, line in enumerate(lines):
        is_line_empty = not line or line[0] == '#'
        is_line_character_name = "\tname = " in line # Marks beginning of character
        is_line_canon_child = " C-Child2" in line # Marks character as canon child
        is_line_block_start = "{" in line
        is_line_block_end = "}" in line

        if is_line_empty:
            continue

        # Setup reading new character
        if is_line_character_name:
            # Print previous character
            if is_reading_character:
                characters[character["id"]] = character
            is_reading_character = False

            # character = Character()
            character = init_character()

            if is_line_canon_child:
                is_reading_character = True

        # Read character
        if is_reading_character:
            is_after_adulthood = False

            if is_line_block_start:
                if text.match_date(line.strip()):
                    current_year_block = text.extract_date_block_year(line.strip())
                    is_after_adulthood = character["birth"] > 0 and current_year_block > character["birth"] + 16
            elif is_line_block_end:
                current_year_block = 0

            # History after adulthood (16+) should be ignored
            if is_after_adulthood:
                continue

            # Some history after the child's birth should be ignored
            is_birth_block = current_year_block == 0 or current_year_block == character["birth"]

            if "=" in line:
                key, value = line.split("=", 1)
                key, value = key.strip(), value.split("#", 1)[0].strip() # Remove comments and whitespaces

                # ID
                if key == "name":
                    character["id"] = lines[i - 1].split(" = ")[0]
                    character["name"]["primary"] = value
                # House
                elif key in ["dynasty", "dynasty_house"]:
                    character["house"] = value
                    # character["house"] = line.split(" = ")[1].split(" #")[0]
                    # if "dynn_" in character["house"]:
                    #     character["house"] = character["house"].split("dynn_")[1]
                    # if "house_" in character["house"]:
                    #     character["house"] = character["house"].split("house_")[1]
                    # if character["flag"] == "FLAG_MISSING":
                    #     character["flag"] = character["name"]["primary"].lower().split("\n")[0] + "_" + character["house"].lower().split("\n")[0]
                # Gender
                elif key == "female":
                    if value == "yes":
                        character["is_female"] = True
                # Father
                elif key == "father":
                    if character["father"] == "":
                        character["father"] = value
                # TODO REFACTOR THIS
                # Real father
                elif key == "real_father" or key == "set_real_father":
                    character["real_father"] = value.split(':')[-1]
                elif key == "effect" and "set_real_father" in value:
                    real_father_id = get_nested_value(value)
                    character["real_father"] = real_father_id.split(':')[-1]
                # Mother
                elif key == "mother" or key == "set_real_mother":
                    character["mother"] = value.split(':')[-1]
                elif key == "effect" and "set_real_mother" in value:
                    mother_id = get_nested_value(value)
                    character["mother"] = mother_id.split(':')[-1]
                # DNA
                elif key == "dna":
                    character["dna"] = value
                # Traits
                elif key == "trait" or key == "add_trait":                
                    if value in childhood_personality_traits_dumpster:
                        character["traits"]["childhood"] = value
                    elif value in personality_traits_dumpster:
                        if len(character["traits"]["education"]) < 4:
                            character["traits"]["education"].append(value)
                    elif value in physical_traits_dumpster:
                        character["traits"]["inherited"].append(value)
                    elif value == "bastard":
                        character["is_bastard"] = True
                elif key == "make_trait_inactive":
                    character["traits"]["inactive"].append(value)
                # Flags
                elif key == "add_character_flag":
                    character["flags"].append(value)
                # Sexuality
                elif key == "sexuality":
                    character["sexuality"] = value
                elif key == "birth":
                    character["birth"] = current_year_block
                # Employer
                elif key == "employer":
                    if is_birth_block:
                        character["employer"] = value
                # Guardian
                elif key == "agot_set_as_ward_history_effect":
                    # TODO gender differences
                    # TODO canon guardians may canonically be too dependent on story events, so maybe only set this if it is set at birth
                    # TODO converting, use_liege_for_heir
                    is_first_guardian = character["guardian"]["primary"]["id"] == ""
                    if is_first_guardian:
                        guardian_id = get_nested_value(value)
                        character["guardian"]["primary"]["id"] = guardian_id
                # Nickname
                elif key == "give_nickname":
                    if is_birth_block:
                        character["nickname"] = value
                # TODO Scripted appearance flags + traits
                # TODO On birth

    # for character in characters:
    #     continue
        # print(get_birth_effect(character))
        # print(json.dumps(character, sort_keys=True, indent=4))
    
    fathers, mothers = find_ancestries(characters)
    # birth_effects = generate_birth_effects(characters, fathers, mothers)
    story_cycles = generate_story_cycles(characters, fathers, mothers)

    # print(birth_effects)
    print(story_cycles)

folder_path = 'D:/projects/agotcch/generate/characters'
lines = file.read_text_files_to_lines(folder_path)

process_lines()
