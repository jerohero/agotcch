import textwrap

def generate_triggers(characters: dict) -> str:
    triggers = []

    for child_id, child in characters.items():
        trigger = textwrap.dedent(f"""
            is_{child_id} = {{
                OR = {{
                    has_inactive_trait = is_{child_id}
                    AND = {{
                        exists = character:{child_id}
                        this = character:{child_id}
                    }}
                }}
            }}
        """)

        triggers.append(trigger)

    return ''.join(triggers).strip()