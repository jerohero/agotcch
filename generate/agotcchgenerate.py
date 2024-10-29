import os
import json
from util import file, text
import textwrap
from birth_effects import generate_birth_effects
from story_cycles import generate_story_cycles
from script_values import generate_script_values
from dummy_characters import generate_dummy_characters
from triggers import generate_triggers
from traits import generate_traits
from accessories import generate_accessories
from character import process_character
from sheet import export_to_excel
from lookups import *

path = "C:/Users/Jeroen/Documents/Paradox Interactive/Crusader Kings III/mod/agotcch/generate"

def process_dna_lines(lines):
	dnas = []

	for i, line in enumerate(lines):
		if "portrait_info" in line:
			dnas.append(lines[i - 1].split(" = ")[0].replace("\ufeff", ""))

	return dnas

def process_character_lines(lines, dnas):
	current_year_block = 0
	character_start_index = 0

	characters = {}
	exception_characters = [] # Characters that aren't canon children but need their own inactive trait

	for i, line in enumerate(lines):
		if not line or line[0] == '#':
			continue
		
		is_line_character_name = "\tname = " in line

		canon_statuses = ["canon_status_canon", "canon_status_semicanon", "canon_status_mentioned"]
		is_line_canon_child = any(status in line for status in canon_statuses)

		if is_line_character_name:
			character_start_index = i

		if is_line_canon_child:
			character = process_character(lines, character_start_index)

			if character["dragons"]["is_dragonrider"] or character["skipped"]:
				exception_characters.append(character["id"])

			# if character is None:
			#     continue

			has_mother = character["mother"] != ""
			has_father = character["father"] != "" or character["real_father"] != ""

			# Skip characters without parents
			if not has_mother and not has_father:
				continue
			elif not has_mother:
				# TODO handle characters with only a father
				continue
			elif not has_father:
				# TODO handle characters with only a mother (eg Maege Mormont's children)
				continue

			if character["dragons"]["is_dragonrider"] or character["skipped"]:
				exception_characters.append(character["id"])
			
			characters[character["id"]] = character
			print(f'\rProcessed: {character["id"]} - {character["name"]["primary"]}', end='\x1b[2K')

	print(f'\r{len(characters)} characters processed', end='')
	
	fathers, mothers = find_ancestries(characters)

	all_ids = set(characters.keys()).union(fathers.keys(), mothers.keys(), exception_characters)

	# with open(path + '/output/common/story_cycles/agot_canon_children_story_cycles.txt', 'w') as f:
	with open('C:/Users/Jeroen/Documents/GitHub/agot/common/story_cycles/agot_canon_children_story_cycles.txt', 'w', encoding="utf-8-sig") as f:
		print('Generating story cycles...')
		f.write(generate_story_cycles(characters, fathers, mothers))

	# with open(path + '/output/common/scripted_effects/00_agot_scripted_effects_canon_children_birth.txt', 'w') as f:
	with open('C:/Users/Jeroen/Documents/GitHub/agot/common/scripted_effects/00_agot_scripted_effects_canon_children_birth.txt', 'w', encoding="utf-8-sig") as f:
		print('Generating birth effects...')
		f.write(generate_birth_effects(characters, fathers, mothers, dnas))

	# with open(path + '/output/common/script_values/00_agot_canon_children_values.txt', 'w') as f:
	# with open('C:/Users/Jeroen/Documents/GitHub/agot/common/script_values/00_agot_canon_children_values.txt', 'w', encoding="utf-8-sig") as f:
	# 	print('Generating script values...')
	# 	f.write(generate_script_values(characters))

	# with open(path + '/output/history/characters/canon_children_dummy_characters.txt', 'w') as f:
	with open('C:/Users/Jeroen/Documents/GitHub/agot/history/characters/agot_canon_children_dummy_characters.txt', 'w', encoding="utf-8-sig") as f:
		print('Generating dummy characters...')
		f.write(generate_dummy_characters(characters, dnas))

	with open('C:/Users/Jeroen/Documents/GitHub/agot/common/scripted_triggers/agot_scripted_triggers_canon_characters.txt', 'w', encoding="utf-8-sig") as f:
		print('Generating triggers...')
		f.write(generate_triggers(all_ids))
		
	with open('C:/Users/Jeroen/Documents/GitHub/agot/common/traits/00_agot_canon_children_traits.txt', 'w', encoding="utf-8-sig") as f:
		print('Generating traits...')
		f.write(generate_traits(all_ids))

	portrait_modifiers = generate_accessories(all_ids)
	with open('C:/Users/Jeroen/Documents/GitHub/agot/gfx/portraits/portrait_modifiers/02_all_agot_characters.txt', 'w', encoding="utf-8-sig") as f:
		print('Generating portrait modifiers...')
		f.write(portrait_modifiers)

	export_to_excel(characters, "characters_export")


# characters_folder_path = path + '/characters/small'
characters_folder_path = 'C:/Users/Jeroen/Documents/GitHub/agot/history/characters'
excluded_character_files = ['00_agot_char_dragons.txt']
character_lines = file.read_text_files_to_lines(characters_folder_path, excluded_character_files)

dna_folder_path = 'C:/Users/Jeroen/Documents/GitHub/agot/common/dna_data'
excluded_dna_files = ['agot_dna_dragons.txt']
dna_lines = file.read_text_files_to_lines(dna_folder_path, excluded_dna_files)

dnas = process_dna_lines(dna_lines)
process_character_lines(character_lines, dnas)
