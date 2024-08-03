import os
import json
from util import file, text
import textwrap


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
    

def get_birth_effect(character):
    indent = '    '

    def get_culture():
        return 'set_culture_same_as = scope:father\n'

    def get_flags():
        output = 'add_character_flag = has_scripted_appearance\n'

        if len(character["flags"]) > 0:
            for flag in character["flags"]:
                output += f'add_character_flag = {flag}\n'

        return output

    def get_inactive_traits():
        output = 'make_trait_inactive = scripted_appearance\n'

        if len(character["traits"]["inactive"]) > 0:
            for trait in character["traits"]["inactive"]:
                output += f'make_trait_inactive = {trait}\n'

        return output

    def get_sexuality():
        if character["sexuality"]:
            return f'set_sexuality = {character["sexuality"]}\n'
        
        return ''

    def get_inherited_traits():
        output = ''

        if character["traits"]["inherited"]:
            for trait in character["traits"]["inherited"]:
                output += f'add_trait = {trait}'

        return output

    def get_childhood_traits():
        output = ''

        if character["traits"]["childhood"] != "":
            output += f'\n\nagot_canon_children_schedule_trait_effect = {{ TRAIT = flag:{character["traits"]["childhood"]} AGE = childhood_personality_age }}\n'

        if len(character["traits"]["education"]) > 0:
            for i, trait in enumerate(character["traits"]["education"]):
                output += f'agot_canon_children_schedule_trait_effect = {{ TRAIT = flag:{trait} AGE = agot_canon_children_trait_{i + 1}_year }}\n'

        return output

    def get_canon_guardian():
        if character["guardian"]["primary"]["id"]:
            return ''

    def inject_data():
        output = '\n'
        output += get_culture()
        output += get_flags()
        output += get_inactive_traits()
        output += get_sexuality()
        output += get_inherited_traits()
        output += get_canon_guardian()
        output += get_childhood_traits()

        return textwrap.indent(output, indent + indent + indent).rstrip()

    birth_effect = textwrap.dedent(f"""
        # {character["name"]["primary"]} - {character["id"]}
        agot_canon_children_{character["id"]}_birth_effect = {{
            scope:child = {{
                agot_canon_children_after_birth_effect = {{
                    NAME_PRIMARY = "{character["name"]["primary"]}"
                    NAME_ALT = "{character["name"]["alt"]}"
                    FLAG = "is_{character["id"]}"
                    DNA = "Dummy_{character["dna"]}"
                }}
            }}
            {inject_data()}
        }}
    """)

    return birth_effect

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
        "config": [
            { "prevent_pregnancy": False }
        ]
    }

def get_nested_value(value):
    return value[value.find('=') + 1 : value.find('}')].strip() # eg. x = { y = z }

def process_lines():
    is_reading_character = False
    current_year_block = 0

    characters = []

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
                characters.append(character)
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
                    character["father"] = value
                # Real father
                elif key == "effect" and "set_real_father" in value:
                    real_father_id = get_nested_value(value)
                    character["real_father"] = real_father_id
                # Mother
                elif key == "mother":
                    character["mother"] = value
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

    for character in characters:
        continue
        # print(get_birth_effect(character))
        # print(json.dumps(character, sort_keys=True, indent=4))
    
    generate_family_trees(characters)

def group_by_parent(children, parent_id_cb):
    parent_dict = {}

    for child in children:
        child_id = child["id"]
        parent_id = parent_id_cb(child)

        if parent_id not in parent_dict:
            parent_dict[parent_id] = []
        parent_dict[parent_id].append(child_id)
        
    # result = [{'id': parent_id, 'children': children} for parent_id, children in parent_dict.items()]

    return parent_dict

# For making sure the child will be set up as a canon mother on birth
def find_mother_chains(mothers):
    mother_chains = []

    for mother_id, child_ids in mothers.items():
        for child_id in child_ids:
            if child_id in mothers:
                mother_chains.append(child_id)


def generate_family_trees(characters):
    def father_id_cb(character):
        return character["real_father"] if character["real_father"] else character["father"]

    def mother_id_cb(character):
        return character["mother"]

    fathers = group_by_parent(characters, father_id_cb)
    mothers = group_by_parent(characters, mother_id_cb)
    mother_chains = find_mother_chains(mothers)

                

folder_path = 'D:/projects/agotcch/generate/characters'
lines = file.read_text_files_to_lines(folder_path)

process_lines()
