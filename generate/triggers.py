import textwrap

def generate_triggers(ids: list) -> str:
	triggers = []

	for character_id in ids:
		trigger = textwrap.dedent(f"""
			is_character_{character_id.lower()} = {{
				OR = {{
					has_inactive_trait = is_{character_id.lower()}
					AND = {{
						exists = character:{character_id}
						this = character:{character_id}
					}}
				}}
			}}
		""")

		triggers.append(trigger)

	return ''.join(triggers).strip()