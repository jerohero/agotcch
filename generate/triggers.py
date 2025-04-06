import textwrap

def generate_triggers(ids: list, triggers_lines) -> str:
	ids = ids[:]
	triggers = []
	base = []

	for i, line in enumerate(triggers_lines):
		if 'CANON CHILDREN TRIGGERS' in line:
			break
		base.append(line)
		if "is_character_" in line:
			trigger_name = line.split("is_character_")[1].split(" =")[0]
			if trigger_name.capitalize() in ids:
				ids.remove(trigger_name.capitalize())
			
	triggers.append(''.join(base))
	triggers.append('# CANON CHILDREN TRIGGERS, AUTO GENERATED')

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
		""").rstrip()

		triggers.append(trigger)

	return ''.join(triggers).rstrip()