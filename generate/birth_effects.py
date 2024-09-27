import textwrap
from lookups import *

INDENT = '    '

def generate_birth_effects(characters: dict, fathers_to_children: dict, mothers_to_children: dict, dnas: list) -> str:
    birth_effects = []
    chained_mothers = find_chained_parents(mothers_to_children)
    chained_fathers = find_chained_parents(fathers_to_children)

    setup_cycles_effect = create_setup_cycles_effect(fathers_to_children).lstrip()
    base_birth_effect = create_base_birth_effect(characters, mothers_to_children)

    for child_id, child in characters.items():
        chained_child_fathers = get_chained_child_fathers(child, characters, mothers_to_children, fathers_to_children, chained_mothers, chained_fathers)

        should_create_twin_birth_effect = False
        birth_effect = ''

        if ("twin" in child["traits"]["inherited"]):
            twins = get_mother_twins(characters, mothers_to_children[child["mother"]])
            should_create_twin_birth_effect = twins[0] != child_id
        
        if not should_create_twin_birth_effect:
            birth_effect = create_birth_effect(child, chained_child_fathers, child_id in dnas)
        else:
            birth_effect = create_twin_birth_effect(child, chained_child_fathers, child_id in dnas)

        birth_effects.append(birth_effect)

    return f"{setup_cycles_effect}{base_birth_effect}\n{''.join(birth_effects).strip()}"

def create_setup_cycles_effect(fathers_to_children: list) -> str:
    setup_effects = [
        textwrap.dedent(f"""
            character:{father} ?= {{
                if = {{
                    limit = {{ is_alive = yes }}
                    create_story = {{ type = story_agot_canon_children_{father.lower()} }}
                }}
            }}
        """) for father in fathers_to_children
    ]

    return textwrap.dedent(f"""
        agot_canon_children_setup_story_cycles_effect = {{
            if = {{
                limit = {{ agot_canon_children_setup_trigger = yes }}
                {textwrap.indent(''.join(setup_effects), INDENT * 4).rstrip()}
            }}
        }}
    """)

def get_mother_twins(characters: dict, mother_to_children: dict) -> list:
    return [child for child in mother_to_children if "twin" in characters[child]["traits"]["inherited"]]

def create_base_birth_effect(characters: dict, mothers_to_children: dict) -> str:
    setup_effects = []

    for i, mother in enumerate(mothers_to_children):
        child_effects = []
        twins = [child for child in mothers_to_children[mother] if "twin" in characters[child]["traits"]["inherited"]]
        twin_birth_effects = []

        for j, child_id in enumerate(mothers_to_children[mother]):
            child = characters[child_id]

            if "twin" in child["traits"]["inherited"]:
                if twin_birth_effects:
                    twin_birth_effects = [] # Will cause issues if there are multiple sets of twins, but it's a rare edge case so we'll just skip it for now
                    continue

                twin_birth_effects = handle_twin_births(child, twins, characters)
            child_effects.append(create_child_effect(j, child, twin_birth_effects))

        setup_effects.append(textwrap.dedent(f"""
            {"if" if i == 0 else "else_if"} = {{
                limit = {{ scope:mother = {{ has_inactive_trait = is_{mother.lower()} }} }}
                {textwrap.indent(''.join(child_effects), INDENT * 4).rstrip()}
            }}
        """))

    return textwrap.dedent(f"""
        agot_canon_children_birth_effect = {{
            scope:child = {{ agot_canon_children_clear_genetic_traits_effect = yes }}
            {textwrap.indent(''.join(setup_effects), INDENT * 3).rstrip()}
        }}
    """)

def get_chained_child_fathers(child: dict, characters: dict, mothers_to_children: dict, fathers_to_children: dict, chained_mothers: list, chained_x: list) -> list:
    chained_child_fathers = []

    if child["is_female"] and child["id"] in chained_mothers:
        chained_child_fathers = get_child_fathers(child, characters, mothers_to_children)
    elif not child["is_female"] and child["id"] in chained_x:
        chained_child_fathers = get_child_fathers(child, characters, fathers_to_children)

    return chained_child_fathers

def get_child_fathers(child: dict, characters: dict, parents_to_children: dict):
    chained_child_fathers = []
    chained_child_ids = parents_to_children[child["id"]]

    for chained_child_id in chained_child_ids:
        chained_child = characters[chained_child_id]
        father = chained_child.get("father") or chained_child.get("real_father") # TODO: should it use real_father if father is not set?

        if father and father not in chained_child_fathers:
            chained_child_fathers.append(father)

    return chained_child_fathers

def create_birth_effect(character: dict, chained_child_fathers: list, has_dna: bool) -> str:
    name_male = character["name"]["primary"] if not character['is_female'] else character["name"]["alt"]
    name_female = character["name"]["primary"] if character['is_female'] else character["name"]["alt"]

    return textwrap.dedent(f"""
        # {character["name"]["primary"]} - {character["id"]}
        agot_canon_children_{character["id"].lower()}_birth_effect = {{
            scope:child = {{
                {"agot_canon_children_after_birth_effect" if has_dna else "agot_canon_children_after_birth_no_dna_effect"} = {{
                    NAME_MALE = "{name_male}"
                    NAME_FEMALE = "{name_female}"
                    TRAIT = is_{character["id"].lower()}{ f'''
                    DNA = Dummy_{character["id"]}''' if has_dna else "" }
                }}
            }}
            {inject_data(character, chained_child_fathers)}
        }}
    """)

def create_twin_birth_effect(character: dict, chained_child_fathers: list, has_dna: bool) -> str:
    name_male = character["name"]["primary"] if not character['is_female'] else character["name"]["alt"]
    name_female = character["name"]["primary"] if character['is_female'] else character["name"]["alt"]

    return textwrap.dedent(f"""
        # {character["name"]["primary"]} - {character["id"]} (Twin)
        agot_canon_children_{character["id"].lower()}_birth_effect = {{
            create_character = {{
                name = "{character['name']['primary']}"
                father = scope:child.father
                mother = scope:child.mother
                gender = {'female' if character['is_female'] else 'male'}
                faith = scope:child.father.faith
                culture = scope:child.father.culture
                dynasty_house = scope:child.father.house
                employer = scope:child.mother.employer

                random_traits = no
                save_scope_as = child
            }}
            hidden_effect = {{
                scope:child = {{
                    {"agot_canon_children_after_birth_effect" if has_dna else "agot_canon_children_after_birth_no_dna_effect"} = {{
                        NAME_MALE = "{name_male}"
                        NAME_FEMALE = "{name_female}"
                        TRAIT = is_{character["id"].lower()}{ f'''
                        DNA = Dummy_{character["id"]}''' if has_dna else "" }
                    }}
                    {inject_data(character, chained_child_fathers, 5)}
                }}
            }}
        }}
    """)

def inject_data(character: dict, chained_child_fathers: list, indent: int = 3) -> str:
    data_parts = [
        get_culture(),
        get_flags(character),
        get_inactive_traits(character),
        get_nickname(character),
        get_sexuality(character),
        get_inherited_traits(character),
        get_canon_guardian(character),
        get_childhood_traits(character),
        get_canon_mother_setup(character, chained_child_fathers),
        get_canon_father_setup(character, chained_child_fathers)
    ]
    return textwrap.indent('\n' + ''.join(data_parts), INDENT * indent).rstrip()

def handle_twin_births(child: dict, twins: list, characters: dict) -> list:
    twin_birth_effects = []
    child_twins = [twin for twin in twins if twin != child["id"] and characters[twin]["birth"] == child["birth"]]
    
    for twin in child_twins:
        twin_birth_effects.append(f"\nagot_canon_children_{twin.lower()}_birth_effect = yes")

    return twin_birth_effects

def create_child_effect(index: int, child: dict, twin_birth_effects: list) -> str:
    return textwrap.dedent(f"""
        {"if" if index == 0 else "else_if"} = {{
            limit = {{ agot_canon_children_check_pregnancy_child_trigger = {{ FLAG = is_{child['id'].lower()} }} }}
            agot_canon_children_{child['id'].lower()}_birth_effect = yes{textwrap.indent(''.join(twin_birth_effects), INDENT * 3).rstrip()}
        }}
    """)

def get_culture():
    return 'set_culture_same_as = scope:father\n'


def get_flags(character):
    flags = ['add_character_flag = has_scripted_appearance']
    
    if character["flags"]:
        flags.extend(f'add_character_flag = {flag}' for flag in character["flags"])

    return '\n'.join(flags) + '\n'


def get_inactive_traits(character):
    traits = ['make_trait_inactive = scripted_appearance']
    
    if character["traits"]["inactive"]:
        traits.extend(f'make_trait_inactive = {trait}' for trait in character["traits"]["inactive"])

    return '\n'.join(traits) + '\n'

def get_nickname(character):
    if character["nickname"]:
        if character["bastard"]["is_known"]:
            return f'agot_canon_children_give_bastard_nickname_effect = {{ NICKNAME = {character["nickname"]} }}\n'
        return f'give_nickname = {character["nickname"]}\n'
    return ''


def get_sexuality(character):
    if character["sexuality"]:
        return f'set_sexuality = {character["sexuality"]}\n'
    return ''


def get_inherited_traits(character):
    if character["traits"]["inherited"]:
        return '\n'.join(f'add_trait = {trait}' for trait in character["traits"]["inherited"]) + '\n'
    return ''


def get_childhood_traits(character):
    output = []

    if character["traits"]["childhood"]:
        output.append(f'agot_canon_children_schedule_trait_effect = {{ TRAIT = flag:{character["traits"]["childhood"]} AGE = childhood_personality_age }}')

    for i, trait in enumerate(character["traits"]["education"]):
        output.append(f'agot_canon_children_schedule_trait_effect = {{ TRAIT = flag:{trait} AGE = agot_canon_children_trait_{i + 1}_year }}')

    return '\n'.join(output) + ('\n' if output else '')


def get_canon_guardian(character):
    # TODO: Implement guardian logic
    return ''


def get_canon_mother_setup(character, chained_child_fathers):
    if not character["is_female"]:
        return ''
    
    mother_setup = []

    for child_father in chained_child_fathers:
        setup = textwrap.dedent(f"""
            agot_canon_children_get_canon_child_scope_effect = {{ TRAIT = is_{child_father.lower()} SCOPE = father_{child_father.lower()} }}
            if = {{
                limit = {{ scope:father_{child_father.lower()} ?= {{ is_alive = yes }} }}
                scope:father_{child_father.lower()} = {{
                    agot_canon_children_setup_mother_effect = {{
                        FATHER = scope:father_{child_father.lower()}
                        MOTHER = scope:child
                        MOTHER_TRAIT = is_{character["id"].lower()}
                        PREVENT_PREGNANCY = yes
                    }}
                }}
            }}
        """)
        mother_setup.append(setup)

    return ''.join(mother_setup)

def get_canon_father_setup(character, chained_child_fathers):
    if character["is_female"]:
        return ''
    
    father_setup = []

    for child_father in chained_child_fathers:
        if child_father == character["id"]:
            father_setup.append(f"\ncreate_story = story_agot_canon_children_{character['id'].lower()}")
        else:
            father_setup.append(textwrap.dedent(f"""
                agot_canon_children_get_canon_child_scope_effect = {{ TRAIT = is_{child_father.lower()} SCOPE = father_{child_father.lower()} }}
                if = {{
                    limit = {{ scope:father_{child_father.lower()} ?= {{ is_alive = yes }} }}
                    scope:father_{child_father.lower()} = {{
                        agot_canon_children_setup_real_father_effect = {{
                            FATHER = scope:father_{child_father.lower()}
                            REAL_FATHER = scope:child
                            REAL_FATHER_TRAIT = is_{character["id"].lower()}
                            REAL_FATHER_VAR = agot_canon_children_real_father_{character["id"].lower()}
                        }}
                    }}
                }}
            """))

    return ''.join(father_setup)