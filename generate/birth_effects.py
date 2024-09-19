import textwrap
from lookups import *

INDENT = '    '

def generate_birth_effects(characters: dict, fathers: list, mothers: dict) -> str:
    birth_effects = []
    chained_mothers = find_chained_mothers(mothers)

    setup_cycles_effect = create_setup_cycles_effect(fathers).lstrip()
    base_birth_effect = create_base_birth_effect(characters, mothers)

    for child_id, child in characters.items():
        chained_fathers = get_chained_fathers(child, child_id, characters, mothers, chained_mothers)
        birth_effect = create_birth_effect(child, chained_fathers)
        birth_effects.append(birth_effect)

    return f"{setup_cycles_effect}{base_birth_effect}\n{''.join(birth_effects).strip()}"

def create_setup_cycles_effect(fathers: list) -> str:
    setup_effects = [
        textwrap.dedent(f"""
            character:{father} ?= {{
                if = {{
                    limit = {{ is_alive = yes }}
                    create_story = {{ type = story_agot_canon_children_{father} }}
                }}
            }}
        """) for father in fathers
    ]

    return textwrap.dedent(f"""
        agot_canon_children_setup_story_cycles_effect = {{
            if = {{
                limit = {{ agot_canon_children_setup_trigger = yes }}
                {textwrap.indent(''.join(setup_effects), INDENT * 4).rstrip()}
            }}
        }}
    """)

def create_base_birth_effect(characters: dict, mothers: dict) -> str:
    setup_effects = []

    for i, mother in enumerate(mothers):
        child_effects = []
        twins = [child for child in mothers[mother] if "twin" in characters[child]["traits"]["inherited"]]
        twin_birth_effects = []

        for j, child_id in enumerate(mothers[mother]):
            child = characters[child_id]
            if "twin" in child["traits"]["inherited"]:
                twin_birth_effects = handle_twin_births(child, twins, characters)
                if twin_birth_effects:
                    continue

            child_effects.append(create_child_effect(j, child, twin_birth_effects))

        setup_effects.append(textwrap.dedent(f"""
            {"if" if i == 0 else "else_if"} = {{
                limit = {{ scope:mother = {{ has_character_flag = is_{mother} }} }}
                {textwrap.indent(''.join(child_effects), INDENT * 4).rstrip()}
            }}
        """))

    return textwrap.dedent(f"""
        agot_canon_children_birth_effect = {{
            scope:child = {{ agot_canon_children_clear_genetic_traits_effect = yes }}
            {textwrap.indent(''.join(setup_effects), INDENT * 3).rstrip()}
        }}
    """)

def get_chained_fathers(child: dict, child_id: str, characters: dict, mothers: dict, chained_mothers: list) -> list:
    chained_fathers = []

    if child["is_female"] and child_id in chained_mothers:
        chained_child_ids = mothers[child_id]
        for chained_child_id in chained_child_ids:
            chained_child = characters[chained_child_id]
            father = chained_child.get("real_father") or chained_child.get("father")
            if father and father not in chained_fathers:
                chained_fathers.append(father)

    return chained_fathers

def create_birth_effect(character: dict, chained_fathers: list) -> str:
    return textwrap.dedent(f"""
        # {character["name"]["primary"]} - {character["id"]}
        agot_canon_children_{character["id"]}_birth_effect = {{
            scope:child = {{
                agot_canon_children_after_birth_effect = {{
                    NAME_PRIMARY = "{character['name']['primary']}"
                    NAME_ALT = "{character['name']['alt']}"
                    FLAG = "is_{character['id']}"
                    DNA = "Dummy_{character['id']}"
                }}
            }}
            {inject_data(character, chained_fathers)}
        }}
    """)

def inject_data(character: dict, chained_fathers: list) -> str:
    data_parts = [
        get_culture(),
        get_flags(character),
        get_inactive_traits(character),
        get_sexuality(character),
        get_inherited_traits(character),
        get_canon_guardian(character),
        get_childhood_traits(character),
        get_canon_mother_setup(character, chained_fathers)
    ]
    return textwrap.indent('\n' + ''.join(data_parts), INDENT * 3).rstrip()

def handle_twin_births(child: dict, twins: list, characters: dict) -> list:
    twin_birth_effects = []
    child_twins = [twin for twin in twins if twin != child["id"] and characters[twin]["birth"] == child["birth"]]
    
    for twin in child_twins:
        twin_birth_effects.append(f"\nagot_canon_children_{twin}_birth_effect = yes")

    return twin_birth_effects

def create_child_effect(index: int, child: dict, twin_birth_effects: list) -> str:
    return textwrap.dedent(f"""
        {"if" if index == 0 else "else_if"} = {{
            limit = {{ agot_canon_children_check_pregnancy_child_trigger = {{ FLAG = is_{child['id']} }} }}
            agot_canon_children_{child['id']}_birth_effect = yes{textwrap.indent(''.join(twin_birth_effects), INDENT * 5).rstrip()}
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
    mother_setup = []

    for father in chained_child_fathers:
        setup = textwrap.dedent(f"""
            agot_canon_children_get_canon_child_scope_effect = {{ FLAG = is_{father} SCOPE = father_{father} }}
            if = {{
                limit = {{ scope:father_{father} ?= {{ is_alive = yes }} }}
                scope:father_{father} = {{
                    agot_canon_children_setup_mother_effect = {{
                        FATHER = scope:father_{father}
                        MOTHER = scope:child
                        MOTHER_FLAG = is_{character["id"]}
                        PREVENT_PREGNANCY = {"yes" if character["config"]["prevent_pregnancy"] else "no"}
                    }}
                }}
            }}
        """)
        mother_setup.append(setup)

    return ''.join(mother_setup)