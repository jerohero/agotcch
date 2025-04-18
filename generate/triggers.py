import gspread
import ckparser as ck
from tqdm.auto import tqdm

gc = gspread.service_account(filename="C:/Users/Jeroen/AppData/Roaming/gspread/api_config.json")
doc = gc.open_by_key("1vfxW06Z-5TSwoMNLLVRlH9lX6QitVW8H3BEKQ_q6HHc")
sh = doc.get_worksheet_by_id(1620397751)

data = sh.get_all_values()
total = len(data)

def generate_triggers(ids: list) -> str:
	results = {}
	genes_templates = {
		"custom_hair": ("hairstyles", "all_hairstyles"),
		"custom_beards": ("beards", "all_beards"),
	}

	for id in ids:
		result = results.setdefault(f"is_character_{id.lower()}", {
			"OR": {
				"has_inactive_trait": f"is_{id.lower()}",
				"AND": {
					"exists": f"character:{id}",
					"this": f"character:{id}",
				}
			}
		})
	for i, row in enumerate(data):
		if not i:
			continue
		# row[17], row[23], row[24]
		# row[21], row[27], row[28]
		(id, name, gender, dynasty, house, birth_date, death_date, culture, religion, *_), dna, canon, custom = row, row[17], row[23], row[24]
		#if canon == "FALSE":
		#    continue
		if not dna and id not in ids:
			continue
		result = results.setdefault(f"is_character_{id.lower()}", {
			"OR": {
				"has_inactive_trait": f"is_{id.lower()}",
				"AND": {
					"exists": f"character:{id}",
					"this": f"character:{id}",
				}
			}
		})
	
	triggers = '\n' + ck.revert(results)

	return triggers


	# ids = ids[:]
	# triggers = []
	# base = []

	# for i, line in enumerate(triggers_lines):
	# 	if 'CANON CHILDREN TRIGGERS' in line:
	# 		break
	# 	base.append(line)
	# 	if "is_character_" in line:
	# 		trigger_name = line.split("is_character_")[1].split(" =")[0]
	# 		if trigger_name.capitalize() in ids:
	# 			ids.remove(trigger_name.capitalize())
			
	# triggers.append(''.join(base))
	# triggers.append('\n# CANON CHILDREN TRIGGERS, AUTO GENERATED')

	# for character_id in ids:
	# 	trigger = textwrap.dedent(f"""
	# 		is_character_{character_id.lower()} = {{
	# 			OR = {{
	# 				has_inactive_trait = is_{character_id.lower()}
	# 				AND = {{
	# 					exists = character:{character_id}
	# 					this = character:{character_id}
	# 				}}
	# 			}}
	# 		}}
	# 	""").rstrip()

	# 	triggers.append(trigger)

	# return ''.join(triggers).rstrip()