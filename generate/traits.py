import textwrap

def generate_traits(characters: dict) -> str:
    traits = []

    for child_id, child in characters.items():
        trait = textwrap.dedent(f"""
            is_{child_id} = {{
                physical = no
                shown_in_ruler_designer = no
                name = trait_hidden
                desc = trait_hidden_desc
                icon = pure_blooded.dds
            }}
        """)

        traits.append(trait)

    return ''.join(traits).strip()