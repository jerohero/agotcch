import os
import re
import json
from util import file, text


class Character:
    def __init__(self):
        self.name = ""

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


def Dumpster_Fire(character):
    bigass_string = ''
    bigass_string += 'agot_canon_children_' + character["flag"] + '_birth_effect = {\n'
    bigass_string += '	scope:child = {\n'
    bigass_string += '		agot_canon_children_after_birth_effect = {\n'
    bigass_string += '			NAME_MALE = "' + character["name"]["male"] + '"\n'
    bigass_string += '			FEMALE_MALE = "' + character["name"]["female"] + '"\n'
    bigass_string += '			FLAG = "is_' + character["flag"] + '"\n'
    bigass_string += '			DNA = "' + character["dna"] + '"\n'
    bigass_string += '		}'
    bigass_string += '\n\n'
    bigass_string += '		set_culture_same_as = scope:father'
    if not "no_sexuality_sex_is_illegal" in character["sexuality"]:
        bigass_string += '\n		set_sexuality = ' + character["sexuality"]
    bigass_string += '\n\n'
    for x in character["traits"]["inactive"]: # Inactive traits
        bigass_string += '		make_trait_inactive = ' + x + '\n'
    for x in character["flags"]: # Flags
        bigass_string += '		add_character_flag = ' + x + '\n'
    for x in character["traits"]["inherited"]: # Genetic Traits
        if x in physical_traits_dumpster:
            bigass_string += '		add_trait = ' + x + '\n'
    bigass_string += '\n'
    trait_count = 1
    for x in character["traits"]["education"]: # Traits
        if x in childhood_personality_traits_dumpster:
            bigass_string += '		agot_canon_children_schedule_trait_effect = { TRAIT = flag:' + x + ' AGE = childhood_personality_age }\n'
        if x in personality_traits_dumpster:
            bigass_string += '		agot_canon_children_schedule_trait_effect = { TRAIT = flag:' + x + ' AGE = agot_canon_children_trait_' + str(trait_count) + '_year }\n'
            trait_count += 1
    bigass_string += '	}\n'
    bigass_string += '}'

    return bigass_string

def init_character():
    return {
        "id": "",
        "flag": "",
        "name": {
            "primary": "",
            "male": "",
            "female": ""
        },
        "is_male": False,
        "house": "",
        "dna": "",
        "sexuality": "",
        "culture": "",
        "employer:": "",
        "traits": {
            "inherited": [],
            "inactive": [],
            "childhood": "",
            "education": []
        },
        "flags": [],
        "guardian": {
            "male": {
                "id": ""
            },
            "female": {
                "id": ""
            },
            "use_liege_for_heir": False,
            "convert_culture": False,
            "convert_religion": False
        },
        "nickname": "",
        "on_birth": "",
        "config": [
            { "prevent_pregnancy": False }
        ]
    }

def process_lines():
    is_reading_character = False

    for i, line in enumerate(lines):
        is_line_empty = not line or line[0] == '#'
        is_line_character_name = "\tname = " in line # Marks beginning of character
        is_line_canon_child = " C-Child2" in line # Marks character as canon child

        if is_line_empty:
            continue

        # Setup reading new character
        if is_line_character_name:
            # Print previous character
            if is_reading_character:
                # print(Dumpster_Fire(character))
                print(json.dumps(character, sort_keys=True, indent=4))

            is_reading_character = False

            # character = Character()
            character = init_character()

            if is_line_canon_child:
                is_reading_character = True

        # Read character
        if is_reading_character:
            if "name = " in line:
                character["id"] = lines[i - 1].split(" = ")[0]
                character["name"]["primary"] = line.split(" = ")[1].split(" #")[0]
            if "dynn_" in line or "house_" in line:
                character["house"] = line.split(" = ")[1].split(" #")[0]
                if "dynn_" in character["house"]:
                    character["house"] = character["house"].split("dynn_")[1]
                if "house_" in character["house"]:
                    character["house"] = character["house"].split("house_")[1]
                if character["flag"] == "FLAG_MISSING":
                    character["flag"] = character["name"]["primary"].lower().split("\n")[0] + "_" + character["house"].lower().split("\n")[0]
            # Gender
            if "female = yes" in line:
                character["is_male"] = False
                character["name"]["female"] = character["name"]["primary"]
            if "female = no" in line:
                character["is_male"] = True
                character["name"]["male"] = character["name"]["primary"]
            # DNA
            if "dna = " in line:
                character["dna"] = text.take_line_value(line)
            # Traits
            if "trait = " in line and not "remove_trait" in line:
                trait = text.take_line_value(line)
                
                if trait in childhood_personality_traits_dumpster:
                     character["traits"]["childhood"] = trait
                elif trait in personality_traits_dumpster:
                    if len(character["traits"]["education"]) < 4:
                        character["traits"]["education"].append(trait)
                elif trait in physical_traits_dumpster:
                    character["traits"]["inherited"].append(trait)
            if "inactive" in line:
                character["traits"]["inactive"].append(text.take_line_value(line))
            if "flag = " in line:
                character["flags"].append(text.take_line_value(line))
            # Sexuality
            if "sexuality = " in line:
                character["sexuality"] = text.take_line_value(line)

# Ścieżka do folderu z plikami tekstowymi
folder_path = 'D:/projects/agotcch/generate/characters'
lines = file.read_text_files_to_lines(folder_path)

process_lines()
