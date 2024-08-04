def group_by_parent(children, parent_id_cb):
    parents = {}

    for child_id, child in children.items():
        child_id = child_id
        parent_id = parent_id_cb(child)

        if parent_id not in parents:
            parents[parent_id] = []
        
        parents[parent_id].append(child_id)

    return parents

# For making sure the child will be set up as a canon mother on birth
def find_chained_mothers(mothers):
    chained_mothers = []

    for mother_id, child_ids in mothers.items():
        for child_id in child_ids:
            if child_id in mothers:
                chained_mothers.append(child_id)

    return chained_mothers

def find_ancestries(characters):
    def father_id_cb(character):
        return character["real_father"] if character["real_father"] else character["father"]

    def mother_id_cb(character):
        return character["mother"]

    fathers = group_by_parent(characters, father_id_cb)
    mothers = group_by_parent(characters, mother_id_cb)

    return fathers, mothers