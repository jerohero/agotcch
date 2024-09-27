import gspread
import ckparser as ck
from tqdm.auto import tqdm
import textwrap

gc = gspread.service_account(filename="C:/Users/Jeroen/AppData/Roaming/gspread/api_config.json")
doc = gc.open_by_key("1vfxW06Z-5TSwoMNLLVRlH9lX6QitVW8H3BEKQ_q6HHc")
sh = doc.get_worksheet_by_id(578315992)

data = sh.get_all_values()
total = len(data)

def generate_accessories(ids: list) -> str:
	results = {}
	genes_templates = {
		"custom_hair": ("hairstyles", "all_hairstyles"),
		"custom_beards": ("beards", "all_beards"),
	}
	for i, row in tqdm(enumerate(data), total=total):
		if not i:
			continue
		(id, name, gender, dynasty, house, birth_date, death_date, culture, religion, has_dna, full_name, *_), dna, canon, custom = row, row[20], row[26], row[27]
		if not dna or custom == "TRUE":
			continue
		dna = ck.parse_text(dna)
		dna = list(dna.values())[0]
		if overrides := dna.get("override"):
			if overrides := overrides.get("portrait_modifier_overrides"):
				result = results.setdefault(id, {
					"dna_modifiers": {
						"accessory": [],
					}, 
					"weight": {
						"base": 0, 
						"modifier": {
							"add": 100,
							"age": {
								"@operator": ">",
								"@value": 4,
							},
							# "exists": f"character:{id}",
							# "this": f"character:{id}",
						},
					},
				})
				if id in ids:
					result["weight"]["modifier"].update({
						f"is_character_{id.lower()}": True,
					})
				else:
					result["weight"]["modifier"].update({
						"exists": f"character:{id}",
						"this": f"character:{id}",
					})
				accessories = result["dna_modifiers"]["accessory"]
				for key, value in overrides.items():
					if "beard" in key and gender == "F":
						continue
					gene, template = genes_templates[key]
					accessory = {
						"mode": "add",
						"gene": gene,
						"template": template,
						"accessory": value,
					}
					if value.endswith("_empty"):
						accessory.pop("accessory")
						accessory.update({
							"template": "no_beard",
							"value": 0,
						})
					elif value == "no_hair":
						accessory.pop("accessory")
						accessory.update({
							"template": "no_hairstyles",
							"value": 0,
						})
					if gender == "F":
						accessory["type"] = "female"
					accessories.append(accessory)


	portrait_modifiers = '\n' + ck.revert(results)
	manual_modifiers = get_manual_modifiers()

	return textwrap.dedent(f'''
historical_characters_accessories = {{
	usage = game
	selection_behavior = max
	priority = 2
	{textwrap.indent(portrait_modifiers, "	")}

	{manual_modifiers}
}}
	''').strip()

def get_manual_modifiers() -> str:
	with open("C:/Users/Jeroen/Documents/GitHub/agot/gfx/portraits/portrait_modifiers/02_all_agot_characters.txt", "r") as file:
		lines = file.readlines()

	start_index = None
	for i, line in enumerate(lines):
		if "#SPECIAL" in line:
			start_index = i - 1
			break
	
	if start_index is not None:
		return ''.join(lines[start_index:-1]).strip()
	else:
		return ""