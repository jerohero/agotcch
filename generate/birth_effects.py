from lookups import *
import textwrap

def generate_birth_effects(characters, fathers, mothers):
    birth_effects = []

    chained_mothers = find_chained_mothers(mothers)

    for child_id, child in characters.items():
        chained_child_fathers = []

        if child["is_female"] and child_id in chained_mothers:
            chained_child_ids = mothers[child_id]

            for chained_child_id in chained_child_ids:
                chained_child = characters[chained_child_id]
                chained_child_father = chained_child["real_father"] or chained_child["father"] # TODO: maybe father should be prioritized?

                if chained_child_father not in chained_child_fathers:
                    chained_child_fathers.append(chained_child_father)

        birth_effect = get_birth_effect(child, chained_child_fathers)

        birth_effects.append(birth_effect)

    return ''.join(birth_effects)

def get_birth_effect(character, chained_child_fathers = []):
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
        has_childhood_traits = character["traits"]["childhood"] != ""
        has_education_traits = len(character["traits"]["education"]) > 0

        if has_childhood_traits or has_education_traits:
            output += '\n\n'

        if has_childhood_traits:
            output += f'agot_canon_children_schedule_trait_effect = {{ TRAIT = flag:{character["traits"]["childhood"]} AGE = childhood_personality_age }}\n'

        if has_education_traits:
            for i, trait in enumerate(character["traits"]["education"]):
                output += f'agot_canon_children_schedule_trait_effect = {{ TRAIT = flag:{trait} AGE = agot_canon_children_trait_{i + 1}_year }}\n'

        return output

    def get_canon_guardian():
        # TODO implement
        if character["guardian"]["primary"]["id"]:
            return ''
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
        output += get_canon_mother_setup()

        return textwrap.indent(output, indent + indent + indent).rstrip()

    # TODO: There can be multiple canon baby fathers
    def get_canon_mother_setup():
        mother_setup = ""

        for father in chained_child_fathers:
            mother_setup += textwrap.dedent(f"""
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

        return mother_setup

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
