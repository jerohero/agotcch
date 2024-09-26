import textwrap

def generate_dummy_characters(characters, dnas):
    dummy_characters = []

    for child_id, child in characters.items():
        if child_id in dnas:
            dummy_characters.append(create_dummy_character(child))

    return ''.join(dummy_characters).lstrip()

def create_dummy_character(child):
    return textwrap.dedent(f"""
        Dummy_{child["id"]} = {{
            name = {child["name"]["primary"]}
            dna = {child["id"]}
            religion = the_seven_main
            culture = northman
            father = Ruin_Empress
            118.1.1 = {{ birth = yes }}
            118.1.2 = {{ death = yes }}
        }}
    """)