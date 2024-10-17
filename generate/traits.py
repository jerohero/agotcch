import textwrap

def generate_traits(ids: list) -> str:
	traits = []

	for character_id in ids:
		trait = textwrap.dedent(f"""
			is_{character_id.lower()} = {{
				physical = no
				shown_in_ruler_designer = no
				name = trait_hidden
				desc = trait_hidden_desc
				icon = pure_blooded.dds
			}}
		""")

		traits.append(trait)

	return ''.join(traits).strip()