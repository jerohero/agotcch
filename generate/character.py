from util import file, text

personality_traits_dumpster = [
	"lustful","chaste","gluttonous","temperate","greedy","generous","lazy","diligent","wrathful","calm","patient","impatient","arrogant",
	"humble","deceitful","honest","craven","brave","shy","gregarious","ambitious","content","arbitrary","just","cynical","zealous",
	"paranoid","trusting","compassionate","callous","sadistic","stubborn","fickle","eccentric","vengeful","forgiving",
] # TODO: authoritative, honorable, rude, ruthless (modded traits without events)

childhood_personality_traits_dumpster = [
	"curious","bossy","pensive","rowdy","charming"
]

physical_traits_dumpster = [
	"beauty_bad_1","beauty_bad_2","beauty_bad_3","beauty_good_1","beauty_good_2","beauty_good_3",
	"intellect_bad_1","intellect_bad_2","intellect_bad_3","intellect_good_1","intellect_good_2","intellect_good_3",
	"physique_bad_1","physique_bad_2","physique_bad_3","physique_good_1","physique_good_2","physique_good_3",
	"pure_blooded","fecund","strong","shrewd","clubfooted","hunchbacked","lisping","stuttering","dwarf","giant",
	"inbred","weak","dull","impotent","spindly","scaly","albino","wheezing","bleeder","infertile","twin"
]

character_flags_excemptions = [
	"has_scripted_appearance",
]

def process_character(lines, character_start_index):
	character = init_character()

	global current_year_block
	global is_birth_block

	current_year_block = 0
	is_after_adulthood = False
	is_birth_block = True

	character["id"] = lines[character_start_index - 1].split(" = ")[0]

	for i, line in enumerate(lines[character_start_index:], start=character_start_index):
		is_line_block_start = "{" in line
		is_line_block_end = "}" in line

		is_next_character = "\tname = " in line and character["name"]["primary"] != ""

		if is_next_character:
			break

		if is_line_block_start:
			if text.match_date(line.strip()):
				current_year_block = text.extract_date_block_year(line.strip())
				is_after_adulthood = character["birth"] > 0 and current_year_block > character["birth"] + 16
		elif is_line_block_end:
			current_year_block = 0

		# History after adulthood (16+) should be ignored
		if is_after_adulthood:
			if "trait = dragonrider" in line:
				character["dragons"]["is_dragonrider"] = True
			return character

		# Some history after the child's birth should be ignored
		is_birth_block = current_year_block == 0 or current_year_block == character["birth"]

		if "=" in line:
			if "# canon_children" in line: # Custom attributes
				line = line.replace("# ", "")

			if "effect = { " in line: # Nested one-liner attributes
				line = line.replace("effect = { ", "")
				if "=" not in line:
					continue
			
			key, value = line.split("=", 1)
			if "=" in value: # Handle other nested attributes
				key, value = value.split("=", 1)
			key, value = key.replace("{", "").replace("}", "").strip(), value.split("#", 1)[0].replace("{", "").replace("}", "").strip() # Remove comments and whitespaces

			if "canon_children_skip" in key and value == "yes":
				character["skipped"] = True
				return character

			if key in key_action_map:
				key_action_map[key](character, value)

		# TODO Scripted appearance flags + traits
		# TODO On birth

	return character

def init_character():
	return {
		"id": "",
		"index": 0,
		"name": {
			"primary": "",
			"alt": ""
		},
		"birth": 0,
		"is_female": False,
		"house": "",
		"father": "",
		"real_father": "",
		"mother": "",
		"sexuality": "",
		"employer:": "",
		"traits": {
			"inherited": [],
			"inactive": [],
			"childhood": "",
			"education": []
		},
		"flags": [],
		"bastard": {
			"is_known": False,
			"real_father_knows": True,
			"surname": ""
		},
		"birth_options": {
			"is_born_sickly": False,
			"is_stillborn": False,
			"mother_dies": False
		},
		"guardian": {
			"primary": {
				"id": ""
			},
			"alt": {
				"id": ""
			},
			"use_liege_for_heir": False,
			"convert_culture": False,
			"convert_religion": False
		},
		"dragons": {
			"is_dragonrider": False
		},
		"nickname": "",
		"on_birth": "",
		"skipped": False,
		"config": { "prevent_pregnancy": False }
	}

def process_name(character, value):
	character["name"]["primary"] = value

def process_house(character, value):
	character["house"] = value

def process_gender(character, value):
	if value == "yes":
		character["is_female"] = True

def process_father(character, value):
	if character["father"] == "":
		character["father"] = value

def process_real_father(character, value):
	character["real_father"] = value.split(':')[-1]

def process_effect_real_father(character, value):
	real_father_id = text.get_nested_value(value)
	character["real_father"] = real_father_id.split(':')[-1]

def process_mother(character, value):
	character["mother"] = value.split(':')[-1]

def process_effect_real_mother(character, value):
	mother_id = text.get_nested_value(value)
	character["mother"] = mother_id.split(':')[-1]

def process_trait(character, value):
	if value in childhood_personality_traits_dumpster:
		character["traits"]["childhood"] = value
	elif value in personality_traits_dumpster:
		if len(character["traits"]["education"]) < 4:
			character["traits"]["education"].append(value)
	elif value in physical_traits_dumpster:
		character["traits"]["inherited"].append(value)
	elif value == "bastard":
		character["bastard"]["is_known"] = True
	elif value == "dragonrider":
		character["dragons"]["is_dragonrider"] = True
	elif value == "sickly":
		if is_birth_block:
			character["birth_options"]["is_born_sickly"] = True

def process_make_trait_inactive(character, value):
	if 'surname_' in value:
		character["bastard"]["surname"] = value
	else:
		character["traits"]["inactive"].append(value)

def process_add_character_flag(character, value):
	if value and value not in character_flags_excemptions:
		character["flags"].append(value)

def process_sexuality(character, value):
	character["sexuality"] = value

def process_birth(character, value):
	character["birth"] = current_year_block

def process_employer(character, value):
	if is_birth_block:
		character["employer"] = value

def process_guardian(character, value):
	is_first_guardian = character["guardian"]["primary"]["id"] == ""
	if is_first_guardian:
		guardian_id = text.get_nested_value(value)
		character["guardian"]["primary"]["id"] = guardian_id

def process_nickname(character, value):
	if is_birth_block:
		character["nickname"] = value

def process_death(character, value):
	is_stillborn = value in ["yes", "{ death_reason = death_delivery }"]
	character["birth_options"]["is_stillborn"] = True if is_stillborn else False

def process_canon_children_mother_dies(character, value):
	character["birth_options"]["mother_dies"] = True if value == "yes" else False

def process_canon_children_alt_name(character, value):
	character["name"]["alt"] = value

def process_canon_children_real_father_knows(character, value):
	character["bastard"]["real_father_knows"] = True if value == "yes" else False

key_action_map = {
	"name": process_name,
	"dynasty": process_house,
	"dynasty_house": process_house,
	"female": process_gender,
	"father": process_father,
	"real_father": process_real_father,
	"set_real_father": process_real_father,
	"mother": process_mother,
	"set_real_mother": process_mother,
	"trait": process_trait,
	"add_trait": process_trait,
	"make_trait_inactive": process_make_trait_inactive,
	"add_character_flag": process_add_character_flag,
	"sexuality": process_sexuality,
	"birth": process_birth,
	"employer": process_employer,
	"agot_set_as_ward_history_effect": process_guardian,
	"give_nickname": process_nickname,
	"death": process_death,
	"canon_children_mother_dies": process_canon_children_mother_dies,
	"canon_children_alt_name": process_canon_children_alt_name,
	"canon_children_real_father_knows": process_canon_children_real_father_knows
}