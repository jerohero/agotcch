def group_by_parent(children, parent_id_cb):
	parents = {}

	for child_id, child in children.items():
		child_id = child_id
		parent_id = parent_id_cb(child)

		if parent_id is None:
			continue

		if parent_id not in parents:
			parents[parent_id] = []
		
		parents[parent_id].append(child_id)

	return parents

# For making sure the child will be set up on birth
def find_chained_parents(parents):
	chained_parents = []

	for parent_id, child_ids in parents.items():
		for child_id in child_ids:
			if child_id in parents:
				chained_parents.append(child_id)

	return chained_parents

def find_ancestries(characters):
	def father_id_cb(character):
		return character["father"] if character["father"] else character["real_father"]
	
	def real_father_id_cb(character):
		return character["real_father"] if character["real_father"] else None

	def mother_id_cb(character):
		return character["mother"]

	fathers = group_by_parent(characters, father_id_cb)
	real_fathers = group_by_parent(characters, real_father_id_cb)
	mothers = group_by_parent(characters, mother_id_cb)

	fathers = dict(sorted(fathers.items(), key=lambda item: item[0]))
	real_fathers = dict(sorted(real_fathers.items(), key=lambda item: item[0]))
	mothers = dict(sorted(mothers.items(), key=lambda item: item[0]))

	return fathers, mothers, real_fathers