import textwrap

base_values = textwrap.dedent(f"""
    # Years
    agot_canon_children_guardian_year = 3
    agot_canon_children_trait_1_year = 9
    agot_canon_children_trait_2_year = 11
    agot_canon_children_trait_3_year = 13
    agot_canon_children_trait_4_year = 14

    # Intervals
    agot_canon_children_stories_cycle_months = 4
    agot_canon_children_pregnancies_cycle_months = 4
    agot_canon_children_pregnancy_duration_months = 10

    agot_canon_children_pregnancy_modifier_duration = {{ value = agot_canon_children_pregnancies_cycle_months add = 1 }}

    # Gender chances
    agot_canon_children_female_female_chance = {{
        value = 0
        if = {{
            limit = {{ has_game_rule = agot_canon_children_gender_accurate }}
            add = {{ value = 100 }}
        }}
        else_if = {{
            limit = {{ has_game_rule = agot_canon_children_gender_semi_accurate }}
            add = {{ value = 75 }}
        }}
        else_if = {{
            limit = {{ has_game_rule = agot_canon_children_gender_random }}
            add = {{ value = 50 }}
        }}
        else = {{
            add = {{ value = 0 }}
        }}
    }}

    agot_canon_children_male_female_chance = {{
        value = 0
        if = {{
            limit = {{ has_game_rule = agot_canon_children_gender_accurate }}
            add = {{ value = 0 }}
        }}
        else_if = {{
            limit = {{ has_game_rule = agot_canon_children_gender_semi_accurate }}
            add = {{ value = 25 }}
        }}
        else_if = {{
            limit = {{ has_game_rule = agot_canon_children_gender_random }}
            add = {{ value = 50 }}
        }}
        else = {{
            add = {{ value = 100 }}
        }}
    }}

    # Birth years
""")

def generate_script_values(characters):
    script_values = []

    for child_id, child in characters.items():
        script_values.append(create_child_script_value(child))

    return (base_values + ''.join(script_values)).strip()

def create_child_script_value(child):
    return textwrap.dedent(f"""
        agot_canon_children_birth_year_{child["id"].lower()} = {child["birth"]}
        agot_canon_children_birth_year_{child["id"].lower()}_min = {{ value = agot_canon_children_birth_year_{child["id"].lower()} add = -1 }}
    """)