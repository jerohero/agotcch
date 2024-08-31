import textwrap
from lookups import *

indent = '    '

def generate_birth_effects(characters, fathers, mothers):
    birth_effects = []
    chained_mothers = find_chained_mothers(mothers)

    setup_cycles_effect = create_setup_cycles_effect(fathers)
    base_birth_effect = create_base_birth_effect(mothers)

    for child_id, child in characters.items():
        chained_child_fathers = get_chained_child_fathers(child, child_id, characters, mothers, chained_mothers)
        birth_effect = create_birth_effect(child, chained_child_fathers)
        birth_effects.append(birth_effect)

    return ''.join(birth_effects).strip()

def create_setup_cycles_effect(fathers):
    setup_effects = []

    for father in fathers:
        setup_effects.append(textwrap.dedent(f"""
            character:{father} ?= {{
                if = {{
                    limit = {{ is_alive = yes }}
                    create_story = {{ type = story_agot_canon_children_{father} }}
                }}
            }}
        """))

    return textwrap.dedent(f"""
        agot_canon_children_setup_story_cycles_effect = {{
            if = {{
                limit = {{
                    agot_canon_children_setup_trigger = yes
                }}
                {textwrap.indent(''.join(setup_effects), indent * 4).rstrip()}
            }}
        }}
    """)

def create_base_birth_effect(mothers):
    setup_effects = []

    for i, mother in enumerate(mothers):
        child_effects = []

        for j, child in enumerate(mothers[mother]):
            # TODO HANDLE TWIN
            child_effects.append(textwrap.dedent(f"""
                {"if" if j == 0 else "else_if"} = {{
                    limit = {{ agot_canon_children_check_pregnancy_child_trigger = {{ FLAG = is_{child} }} }}
                    agot_canon_children_{child}_birth_effect = yes
                }}
            """).rstrip())

        setup_effects.append(textwrap.dedent(f"""
            {"if" if i == 0 else "else_if"} = {{
                limit = {{
                    scope:mother = {{ has_character_flag = is_{mother} }}
                }}
                {textwrap.indent(''.join(child_effects), indent * 4).rstrip()}
            }}
        """))

    return textwrap.dedent(f"""
        agot_canon_children_birth_effect = {{
            scope:child = {{
                agot_canon_children_clear_genetic_traits_effect = yes
            }}
            {textwrap.indent(''.join(setup_effects), indent * 3).rstrip()}
        }}
    """)

def get_chained_child_fathers(child, child_id, characters, mothers, chained_mothers):
    chained_child_fathers = []

    if child["is_female"] and child_id in chained_mothers:
        chained_child_ids = mothers[child_id]

        for chained_child_id in chained_child_ids:
            chained_child = characters[chained_child_id]
            chained_child_father = chained_child["real_father"] or chained_child["father"]

            if chained_child_father not in chained_child_fathers:
                chained_child_fathers.append(chained_child_father)

    return chained_child_fathers


def create_birth_effect(character, chained_child_fathers):
    return textwrap.dedent(f"""
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
            {inject_data(character, chained_child_fathers)}
        }}
    """)


def inject_data(character, chained_child_fathers):
    output = '\n'
    output += get_culture()
    output += get_flags(character)
    output += get_inactive_traits(character)
    output += get_sexuality(character)
    output += get_inherited_traits(character)
    output += get_canon_guardian(character)
    output += get_childhood_traits(character)
    output += get_canon_mother_setup(character, chained_child_fathers)

    return textwrap.indent(output, indent * 3).rstrip()


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
