import textwrap

def generate_story_cycles(characters, fathers, mothers):
    story_cycles = []

    print(fathers)

    for father_id, child_ids in fathers.items():
        story_cycle = get_story_cycle(characters, father_id, child_ids)

        story_cycles.append(story_cycle)

    return ''.join(story_cycles)

def get_story_cycle(characters, father_id, child_ids):
    indent = '    '

    mother_ids = list(set(
        characters[child_id]["mother"] for child_id in child_ids
    ))
    real_father_ids = list(set(
        characters[child_id]["real_father"] for child_id in child_ids if characters[child_id]["real_father"]
    ))

    def get_setup():
        setup = []

        setup.append(textwrap.dedent(f"""
            agot_canon_children_setup_father_effect = {{
                FATHER = story_owner
                FATHER_FLAG = is_{father_id}
            }}
        """).lstrip())

        for mother_id in mother_ids:
            setup.append(textwrap.dedent(f"""
                agot_canon_children_setup_mother_effect = {{
                    FATHER = story_owner
                    MOTHER = character:{mother_id}
                    MOTHER_FLAG = is_{mother_id}
                    PREVENT_PREGNANCY = yes
                }}
            """))

        for i, real_father_id in enumerate(real_father_ids):
            setup.append(textwrap.dedent(f"""
                agot_canon_children_setup_real_father_effect = {{
                    FATHER = story_owner
                    REAL_FATHER = character:{real_father_id}
                    REAL_FATHER_FLAG = is_{real_father_id}
                    REAL_FATHER_VAR = agot_canon_children_real_father_{i + 1}
                }}
            """))

        return textwrap.indent('\n'.join(setup), indent * 2).rstrip()

    def get_pregnancy_effects():
        effects = []

        for mother_i, mother_id in enumerate(mother_ids):
            def get_children_effects():
                children_effects = []

                for child_i, child_id in enumerate(child_ids):
                    child = characters[child_id]
                    if child["mother"] == mother_id:
                        children_effects.append(textwrap.dedent(f"""
                            # {child_id}
                            {"if" if child_i == 0 else "else_if"} = {{
                                limit = {{
                                    agot_canon_children_child_pregnancy_trigger = {{
                                        ID = {child_id}
                                        FLAG = is_{child_id}
                                        BIRTH_YEAR = agot_canon_children_birth_year_{child_id}
                                    }}
                                }}
                                agot_canon_children_force_pregnancy_basic_effect = {{
                                    CHILD_FLAG = is_{child_id}
                                    IS_FEMALE = {"yes" if child["is_female"] else "no"}
                                }}
                            }}
                        """))

                return textwrap.indent('\n'.join(children_effects), indent * 5).rstrip()

            effects.append(textwrap.dedent(f"""
                # {mother_id}
                {"if" if mother_i == 0 else "else_if"} = {{
                    limit = {{
                        has_character_flag = is_{mother_id}
                        scope:canon_father = {{
                            agot_canon_children_force_pregnancy_spouse_trigger = {{
                                SPOUSE = scope:canon_mother
                            }}
                        }}
                    }}
                    {get_children_effects()}
                }}
            """))

        return textwrap.indent('\n'.join(effects), indent * 4).rstrip()

    story_cycle = textwrap.dedent(f"""
        story_agot_canon_children_{father_id} = {{
            on_setup = {{
{textwrap.indent(get_setup(), indent * 2)}
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
{textwrap.indent(get_pregnancy_effects(), indent * 4)}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """).rstrip()

    return story_cycle