import textwrap


def generate_story_cycles(characters, fathers, mothers):
    story_cycles = []

    for father_id, child_ids in fathers.items():
        story_cycle = create_story_cycle(characters, father_id, child_ids)
        story_cycles.append(story_cycle)

    return ''.join(story_cycles).strip()


def create_story_cycle(characters, father_id, child_ids):
    indent = '    '

    mother_ids = {characters[child_id]["mother"] for child_id in child_ids}
    real_father_ids = {characters[child_id]["real_father"] for child_id in child_ids if characters[child_id]["real_father"]}

    setup = generate_setup(father_id, mother_ids, real_father_ids, child_ids, characters, indent)
    pregnancy_effects = generate_pregnancy_effects(characters, child_ids, mother_ids, indent)

    return textwrap.dedent(f"""
        story_agot_canon_children_{father_id.lower()} = {{
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
    """)


def generate_setup(father_id, mother_ids, real_father_ids, child_ids, characters, indent):
    setup_lines = [
        textwrap.dedent(f"""
        agot_canon_children_setup_father_effect = {{
            FATHER = story_owner
            FATHER_TRAIT = is_{father_id.lower()}
        }}
        """)
    ]

    for mother_id in mother_ids:
        should_prevent_pregnancy = all(
            not (child["bastard"]["is_known"] and (child["father"] == father_id or (child["real_father"] == father_id and child["father"] == ""))) # Does not have a known bastard
            for child in (characters[child_id] for child_id in child_ids if characters[child_id]["mother"] == mother_id)
        )

        setup_lines.append(textwrap.dedent(f"""
            agot_canon_children_setup_mother_effect = {{
                FATHER = story_owner
                MOTHER = character:{mother_id}
                MOTHER_TRAIT = is_{mother_id.lower()}
                PREVENT_PREGNANCY = {"yes" if should_prevent_pregnancy else "no"}
            }}
        """))

    for real_father_id in real_father_ids:
        if real_father_id == father_id:
            continue
            
        setup_lines.append(textwrap.dedent(f"""
            agot_canon_children_setup_real_father_effect = {{
                FATHER = story_owner
                REAL_FATHER = character:{real_father_id}
                REAL_FATHER_TRAIT = is_{real_father_id.lower()}
                REAL_FATHER_VAR = agot_canon_children_real_father_{real_father_id.lower()}
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
    is_female = "yes" if child["is_female"] else "no"
    is_bastard_with_assumed_father = child["real_father"] != "" and child["father"] != ""

    birth_flag = "birth_will_go_smoothly"

    if child["birth_options"]["is_stillborn"]:
        birth_flag = "birth_will_be_stillborn"
    elif child["birth_options"]["mother_dies"]:
        birth_flag = "agot_birth_mother_will_die"
    elif child["birth_options"]["is_born_sickly"]:
        birth_flag = "birth_child_will_become_sickly"

    if child["real_father"] == "":
        effect = textwrap.dedent(f"""
            agot_canon_children_force_pregnancy_effect = {{
                CHILD_FLAG = is_{child["id"].lower()}
                IS_FEMALE = {is_female}
                FATHER = scope:canon_father
                BIRTH_FLAG = {birth_flag}
            }}
        """)
    else:
        effect = textwrap.dedent(f"""
            agot_canon_children_force_bastard_pregnancy_basic_effect = {{
                CHILD_FLAG = is_{child["id"].lower()}
                IS_FEMALE = {is_female}
                REAL_FATHER = {
                    f"scope:canon_father.var:agot_canon_children_real_father_{child['real_father'].lower()}" if is_bastard_with_assumed_father  
                    else "scope:canon_father"
                }
                REAL_FATHER_KNOWS = {"yes" if child["bastard"]["real_father_knows"] else "no"}	
                KNOWN_BASTARD = {"yes" if child["bastard"]["is_known"] else "no"}
            }}
        """)

    return textwrap.indent(effect.strip(), indent * 5).strip()


def generate_pregnancy_effects(characters, child_ids, mother_ids, indent):
    effects = []

    for mother_index, mother_id in enumerate(mother_ids):
        first_child = characters[child_ids[0]]
        mother_condition = "if" if mother_index == 0 else "else_if"

        pregnancy_trigger = generate_pregnancy_trigger(first_child["bastard"]["is_known"], indent)
        children_effects = generate_children_effects(characters, child_ids, mother_id, indent)

        effects.append(textwrap.dedent(f"""
            # {mother_id}
            {mother_condition} = {{
                limit = {{
                    has_inactive_trait = is_{mother_id.lower()}
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

    twin_pointer = None

    for child_index, child_id in enumerate(child_ids):
        child = characters[child_id]

        if child["mother"] == mother_id:
            child_condition = "if" if child_index == 0 else "else_if"
            pregnancy_effect = generate_pregnancy_effect(child, indent)

            if "twin" in child["traits"]["inherited"]:
                # Only create an effect for the first child of a pair of twins
                if twin_pointer and twin_pointer["birth"] == child["birth"]:
                    continue
                twin_pointer = child

            children_effects.append(textwrap.dedent(f"""
                # {child_id}{" (twin)" if "twin" in child["traits"]["inherited"] else ""} 
                {child_condition} = {{
                    limit = {{
                        agot_canon_children_child_pregnancy_trigger = {{
                            ID = {child_id}
                            TRAIT = is_{child_id.lower()}
                            BIRTH_YEAR = agot_canon_children_birth_year_{child_id.lower()}
                        }}
                    }}
                    {pregnancy_effect}
                }}
            """).rstrip())

    children_effects.append(textwrap.dedent(f"""
        # Lifecycle
        agot_canon_children_life_cycle_effect = {{
            MOTHER = scope:canon_mother
            FINAL_CHILD_TRAIT = is_{child_ids[-1].lower()}
            FINAL_CHILD_ID = {child_ids[-1]}
        }}
    """))

    return textwrap.indent('\n'.join(children_effects), indent * 4).rstrip()