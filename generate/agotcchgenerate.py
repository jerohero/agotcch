import os
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
        "name": {
            "primary": "",
            "male": "",
            "female": ""
        },
        "birth": 0,
        "is_female": False,
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
    current_year_block = 0

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
                # print(Dumpster_Fire(character))
                print(json.dumps(character, sort_keys=True, indent=4))

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

            if is_after_adulthood:
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key, value = key.strip(), value.split("#", 1)[0].strip() # Remove comments and whitespaces

                # ID
                if key == "name":
                    character["id"] = lines[i - 1].split(" = ")[0]
                    character["name"]["primary"] = value
                    character["name"]["male"] = value # Set male name before knowing gender
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
                        character["name"]["female"] = character["name"]["primary"]
                        character["name"]["male"] = ""
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

# Ścieżka do folderu z plikami tekstowymi
folder_path = 'D:/projects/agotcch/generate/characters'
lines = file.read_text_files_to_lines(folder_path)

process_lines()
