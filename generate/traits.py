import gspread
import ckparser as ck
from tqdm.auto import tqdm

gc = gspread.service_account(filename="C:/Users/Jeroen/AppData/Roaming/gspread/api_config.json")
doc = gc.open_by_key("1vfxW06Z-5TSwoMNLLVRlH9lX6QitVW8H3BEKQ_q6HHc")
sh = doc.get_worksheet_by_id(1620397751)

data = sh.get_all_values()
total = len(data)

def generate_traits(ids: list) -> str:
	results = {}
	genes_templates = {
		"custom_hair": ("hairstyles", "all_hairstyles"),
		"custom_beards": ("beards", "all_beards"),
	}

	# for id in ids:
	# 	result = results.setdefault(f"is_{id.lower()}", {
	# 		"physical": "no",
	# 		"shown_in_ruler_designer": "no",
	# 		"name": "trait_hidden",
	# 		"desc": "trait_hidden_desc",
	# 		"icon": "pure_blooded.dds",
	# 	})
	for i, row in enumerate(data):
		if not i:
			continue
		
		# row[17], row[23], row[24]
		# row[21], row[27], row[28]
		(id, name, gender, dynasty, house, birth_date, death_date, culture, religion, *_), dna, canon, custom = row, row[17], row[23], row[24]
		#if canon == "FALSE":
		#    continue
		if not dna:
			continue
		result = results.setdefault(f"is_{id.lower()}", {
			"physical": "no",
			"shown_in_ruler_designer": "no",
			"name": "trait_hidden",
			"desc": "trait_hidden_desc",
			"icon": "pure_blooded.dds",
		})

	traits = '\n' + ck.revert(results)

	return traits


