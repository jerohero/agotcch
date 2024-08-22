import textwrap


def generate_story_cycles(characters, fathers, mothers):
    story_cycles = []

    for father_id, child_ids in fathers.items():
        story_cycle = create_story_cycle(characters, father_id, child_ids)
        story_cycles.append(story_cycle)

    return ''.join(story_cycles)


def create_story_cycle(characters, father_id, child_ids):
    indent = '    '

    mother_ids = {characters[child_id]["mother"] for child_id in child_ids}
    real_father_ids = {
        characters[child_id]["real_father"] for child_id in child_ids if characters[child_id]["real_father"]
    }

    setup = generate_setup(father_id, mother_ids, real_father_ids, indent)
    pregnancy_effects = generate_pregnancy_effects(characters, child_ids, mother_ids, indent)

    return textwrap.dedent(f"""
        story_agot_canon_children_{father_id} = {{
            on_setup = {{
{textwrap.indent(setup, indent * 2)}
            }}

            on_end = {{ }}
            on_owner_death = {{ agot_canon_children_on_owner_death_effect = yes }}

            # Pregnancies
            effect_group = {{
                months = agot_canon_children_pregnancies_cycle_months

                triggered_effect = {{
                    effect = {{
                        story_owner = {{
                            save_scope_as = canon_father
                            every_in_list = {{
                                variable = canon_mothers
                                save_scope_as = canon_mother
                                {textwrap.indent(pregnancy_effects, indent * 4)}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """).rstrip()


def generate_setup(father_id, mother_ids, real_father_ids, indent):
    setup_lines = [
        textwrap.dedent(f"""
        agot_canon_children_setup_father_effect = {{
            FATHER = story_owner
            FATHER_FLAG = is_{father_id}
        }}
        """)
    ]

    for mother_id in mother_ids:
        setup_lines.append(textwrap.dedent(f"""
            agot_canon_children_setup_mother_effect = {{
                FATHER = story_owner
                MOTHER = character:{mother_id}
                MOTHER_FLAG = is_{mother_id}
                PREVENT_PREGNANCY = yes
            }}
        """))

    for real_father_id in real_father_ids:
        setup_lines.append(textwrap.dedent(f"""
            agot_canon_children_setup_real_father_effect = {{
                FATHER = story_owner
                REAL_FATHER = character:{real_father_id}
                REAL_FATHER_FLAG = is_{real_father_id}
                REAL_FATHER_VAR = agot_canon_children_real_father_{real_father_id}
            }}
        """))

    return textwrap.indent('\n'.join(line.strip() for line in setup_lines), indent * 2).rstrip()


def generate_pregnancy_trigger(is_first_child_bastard, indent):
    if is_first_child_bastard:
        trigger = textwrap.dedent("""
            agot_canon_children_force_pregnancy_happy_accident_trigger = {
                MOTHER = scope:canon_mother
            }
        """)
    else:
        trigger = textwrap.dedent("""
            agot_canon_children_force_pregnancy_spouse_trigger = {
                SPOUSE = scope:canon_mother
            }
        """)

    return textwrap.indent(trigger.strip(), indent * 6).strip()


def generate_pregnancy_effect(child, indent):
    if child["real_father"] == "":
        # TODO: stillborn, death on childbirth etc
        effect = textwrap.dedent(f"""
            agot_canon_children_force_pregnancy_basic_effect = {{
                CHILD_FLAG = is_{child["id"]}
                IS_FEMALE = {"yes" if child["is_female"] else "no"}
            }}
        """)
    else:
        # TODO: real father knows & known bastard
        effect = textwrap.dedent(f"""
            agot_canon_children_force_bastard_pregnancy_basic_effect = {{
                CHILD_FLAG = is_{child["id"]}
                IS_FEMALE = {"yes" if child["is_female"] else "no"}
                REAL_FATHER = scope:canon_father.var:agot_canon_children_real_father_{child["real_father"]}
                REAL_FATHER_KNOWS = yes
                KNOWN_BASTARD = no
            }}
        """)

    return textwrap.indent(effect.strip(), indent * 5).strip()


def generate_pregnancy_effects(characters, child_ids, mother_ids, indent):
    effects = []

    for mother_index, mother_id in enumerate(mother_ids):
        first_child = characters[child_ids[0]]
        mother_condition = "if" if mother_index == 0 else "else_if"

        pregnancy_trigger = generate_pregnancy_trigger(first_child["is_bastard"], indent)
        children_effects = generate_children_effects(characters, child_ids, mother_id, indent)

        effects.append(textwrap.dedent(f"""
            # {mother_id}
            {mother_condition} = {{
                limit = {{
                    has_character_flag = is_{mother_id}
                    scope:canon_father = {{
                        {pregnancy_trigger}
                    }}
                }}
                {children_effects}
            }}
        """))

    return textwrap.indent('\n'.join(effects), indent * 4).rstrip()


def generate_children_effects(characters, child_ids, mother_id, indent):
    children_effects = []

    for child_index, child_id in enumerate(child_ids):
        child = characters[child_id]
        if child["mother"] == mother_id:
            child_condition = "if" if child_index == 0 else "else_if"
            pregnancy_effect = generate_pregnancy_effect(child, indent)

            children_effects.append(textwrap.dedent(f"""
                # {child_id}
                {child_condition} = {{
                    limit = {{
                        agot_canon_children_child_pregnancy_trigger = {{
                            ID = {child_id}
                            FLAG = is_{child_id}
                            BIRTH_YEAR = agot_canon_children_birth_year_{child_id}
                        }}
                    }}
                    {pregnancy_effect}
                }}
            """))

    children_effects.append(textwrap.dedent(f"""
        # Lifecycle
        agot_canon_children_life_cycle_effect = {{
            MOTHER = scope:canon_mother
            FINAL_CHILD_FLAG = is_{child_ids[-1]}
            FINAL_CHILD_ID = {child_ids[-1]}
        }}
    """))

    return textwrap.indent('\n'.join(children_effects), indent * 4).rstrip()